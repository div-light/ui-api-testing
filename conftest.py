import os
import re
import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from api.auth_api import register_user
from config.config import UI_BASE
from testdata.credentials import PASSWORD
from utils.logger import logger

ARTIFACTS = Path("artifacts")
HEADLESS = os.getenv("HEADLESS", "1") == "1"


def _new_email():
    return f"testuser{uuid.uuid4().hex[:7]}@user.com"


def _safe(name: str) -> str:
    return re.sub(r"[^\w.-]", "_", name)



def pytest_sessionstart(session):
    if hasattr(session.config, "workerinput"):
        return
    if ARTIFACTS.exists():
        shutil.rmtree(ARTIFACTS)
    for sub in ("screenshots", "videos", "traces"):
        (ARTIFACTS / sub).mkdir(parents=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report) 

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page") or item.funcargs.get("authenticated_page")
        if page:
            shot_dir = ARTIFACTS / "screenshots"
            shot_dir.mkdir(parents=True, exist_ok=True)
            path = shot_dir / f"{_safe(item.name)}.png"
            page.screenshot(path=str(path), full_page=True)
            logger.info("Screenshot saved %s", path)




@contextmanager
def _traced_context(browser, request, **kwargs):
    context = browser.new_context(record_video_dir=str(ARTIFACTS / "videos"), **kwargs)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    try:
        yield context
    finally:
        rep = getattr(request.node, "rep_call", None)
        failed = bool(rep and rep.failed)
        trace_path = None
        if failed:
            trace_dir = ARTIFACTS / "traces"
            trace_dir.mkdir(parents=True, exist_ok=True)
            trace_path = str(trace_dir / f"{_safe(request.node.name)}.zip")
        context.tracing.stop(path=trace_path)
        context.close()



@pytest.fixture(scope="session")
def registered_user():
    email = _new_email()
    register_user(email, PASSWORD)
    return email, PASSWORD


@pytest.fixture(scope="session")
def pw_browser():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def auth_user(pw_browser, registered_user, tmp_path_factory):
    email, password = registered_user
    auth_file = tmp_path_factory.mktemp("auth") / "state.json"
    context = pw_browser.new_context()
    try:
        page = context.new_page()
        page.goto(UI_BASE)
        page.locator("#userEmail").fill(email)
        page.locator("#userPassword").fill(password)
        page.get_by_role("button", name="login").click()
        page.wait_for_url("**/dashboard/**")
        context.storage_state(path=str(auth_file))
    finally:
        context.close()
    return auth_file


@pytest.fixture
def authenticated_page(pw_browser, auth_user, request):
    with _traced_context(pw_browser, request, storage_state=str(auth_user)) as context:
        yield context.new_page()


@pytest.fixture
def page(pw_browser, request):
    with _traced_context(pw_browser, request) as context:
        yield context.new_page()