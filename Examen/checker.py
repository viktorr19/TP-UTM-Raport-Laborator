import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    return f"https://{host.rstrip('/')}/{path.lstrip('/')}"


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.lower().startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}", flush=True)
        print(f"Content-Type: {response.headers.get('Content-Type')}", flush=True)
    except requests.RequestException as error:
        message = str(error).strip() or type(error).__name__
        print(f"Error: {message[:120]}", flush=True)


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        response = requests.get(url, timeout=5)
        content_type = response.headers.get("Content-Type", "")
        return {
            "status": response.status_code,
            "content_type": content_type.split(";", 1)[0],
            "length": len(response.content),
            "server": response.headers.get("Server") or "unknown",
        }
    except requests.RequestException as error:
        message = str(error).strip() or type(error).__name__
        return {"status": None, "error": message[:120]}


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    results = [(site, check_site(site)) for site in SITES]
    successful = [
        (site, result)
        for site, result in results
        if result["status"] == 200
    ]
    successful.sort(key=lambda item: item[1]["length"], reverse=True)

    for site, result in successful:
        print(f"{site} -> 200, {result['length']} octeți", flush=True)

    failed_count = len(results) - len(successful)
    print(f"Reușite: {len(successful)} | Eșuate: {failed_count}", flush=True)


def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        response = requests.get(url, timeout=5)
        response_headers = {name.lower() for name in response.headers}
        present = [
            header for header in SECURITY_HEADERS
            if header.lower() in response_headers
        ]
        missing = [
            header for header in SECURITY_HEADERS
            if header.lower() not in response_headers
        ]
        score = int(len(present) * 100 / len(SECURITY_HEADERS)) if SECURITY_HEADERS else 0
        return {"present": present, "missing": missing, "score": score}
    except requests.RequestException as error:
        message = str(error).strip() or type(error).__name__
        return {"status": None, "error": message[:120]}


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    attempts_made = 0
    last_status = None
    last_error = None

    for _ in range(max(0, attempts)):
        attempts_made += 1
        try:
            response = requests.get(url, timeout=5)
            last_status = response.status_code
            last_error = None
            if last_status < 500:
                return {"status": last_status, "attempts": attempts_made}
        except requests.RequestException as error:
            last_error = str(error).strip() or type(error).__name__

    result = {"status": last_status, "attempts": attempts_made}
    if last_status is None and last_error is not None:
        result["error"] = last_error[:120]
    return result
