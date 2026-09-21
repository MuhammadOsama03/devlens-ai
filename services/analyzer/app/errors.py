from dataclasses import dataclass


@dataclass(frozen=True)
class PublicError:
    code: str
    message: str
    retryable: bool = False


def map_upstream_status(status_code: int) -> PublicError:
    if status_code == 404:
        return PublicError("repository_not_found", "Repository was not found.")
    if status_code in {401, 403}:
        return PublicError("github_access_denied", "GitHub denied access to the repository.")
    if status_code == 429:
        return PublicError("github_rate_limited", "GitHub rate limit was reached.", True)
    if 500 <= status_code:
        return PublicError("github_unavailable", "GitHub is temporarily unavailable.", True)
    return PublicError("github_request_failed", "GitHub could not process the request.")
