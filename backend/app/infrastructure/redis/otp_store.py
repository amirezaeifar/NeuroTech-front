from __future__ import annotations

from datetime import timezone

from redis import Redis, RedisError

from app.core.exceptions import InfrastructureError, OtpCooldownError, OtpRateLimitError
from app.domain.ports.otp_store import OtpRecord, OtpStore, OtpVerificationStatus

_CREATE_SCRIPT = """
local otp_key = KEYS[1]
local rate_key = KEYS[2]
local now = tonumber(ARGV[1])
local resend_at = redis.call('HGET', otp_key, 'resend_available_at')
if resend_at and tonumber(resend_at) > now then
  return -1
end
local requests = redis.call('INCR', rate_key)
if requests == 1 then redis.call('EXPIRE', rate_key, 3600) end
if requests > tonumber(ARGV[2]) then return -2 end
redis.call('HSET', otp_key,
  'purpose', ARGV[3],
  'destination', ARGV[4],
  'code_hash', ARGV[5],
  'created_at', ARGV[1],
  'expires_at', ARGV[6],
  'attempt_count', 0,
  'max_attempts', ARGV[7],
  'request_count', requests,
  'resend_available_at', ARGV[8])
redis.call('EXPIRE', otp_key, tonumber(ARGV[9]))
return requests
"""

_VERIFY_SCRIPT = """
local key = KEYS[1]
if redis.call('EXISTS', key) == 0 then return 0 end
local attempts = tonumber(redis.call('HGET', key, 'attempt_count') or '0')
local maximum = tonumber(redis.call('HGET', key, 'max_attempts') or '1')
if attempts >= maximum then redis.call('DEL', key); return 3 end
local expected = redis.call('HGET', key, 'code_hash')
if expected == ARGV[1] then redis.call('DEL', key); return 1 end
attempts = redis.call('HINCRBY', key, 'attempt_count', 1)
if attempts >= maximum then redis.call('DEL', key); return 3 end
return 2
"""


class RedisOtpStore(OtpStore):
    def __init__(self, client: Redis, namespace: str = "neurotech") -> None:
        self._client = client
        self._namespace = namespace

    def create(
        self,
        record: OtpRecord,
        *,
        ttl_seconds: int,
        max_requests_per_hour: int,
    ) -> None:
        try:
            result = int(
                self._client.eval(
                    _CREATE_SCRIPT,
                    2,
                    self._otp_key(record.purpose, record.destination),
                    self._rate_key(record.destination),
                    self._epoch(record.created_at),
                    max_requests_per_hour,
                    record.purpose,
                    record.destination,
                    record.code_hash,
                    self._epoch(record.expires_at),
                    record.max_attempts,
                    self._epoch(record.resend_available_at),
                    ttl_seconds,
                )
            )
        except RedisError as exc:
            raise InfrastructureError("OTP storage is temporarily unavailable.") from exc
        if result == -1:
            raise OtpCooldownError("Please wait before requesting another code.")
        if result == -2:
            raise OtpRateLimitError("OTP request limit exceeded.")

    def verify_and_consume(
        self, purpose: str, destination: str, candidate_hash: str
    ) -> OtpVerificationStatus:
        try:
            result = int(
                self._client.eval(
                    _VERIFY_SCRIPT,
                    1,
                    self._otp_key(purpose, destination),
                    candidate_hash,
                )
            )
        except RedisError as exc:
            raise InfrastructureError("OTP storage is temporarily unavailable.") from exc
        return {
            0: OtpVerificationStatus.MISSING,
            1: OtpVerificationStatus.VERIFIED,
            2: OtpVerificationStatus.INVALID,
            3: OtpVerificationStatus.ATTEMPTS_EXCEEDED,
        }[result]

    def consume(self, purpose: str, destination: str) -> None:
        try:
            self._client.delete(self._otp_key(purpose, destination))
        except RedisError as exc:
            raise InfrastructureError("OTP storage is temporarily unavailable.") from exc

    def _otp_key(self, purpose: str, destination: str) -> str:
        return f"{self._namespace}:otp:{purpose}:{destination}"

    def _rate_key(self, destination: str) -> str:
        return f"{self._namespace}:otp-rate:{destination}"

    @staticmethod
    def _epoch(value) -> int:
        aware = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        return int(aware.timestamp())
