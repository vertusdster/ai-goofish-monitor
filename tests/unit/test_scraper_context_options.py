"""_default_context_options 的 UA/视口自洽性测试（2026-10-02）。

背景：容器内 Chromium 运行在 Linux x86_64 + SwiftShader，却声明 Android Nexus 5
移动 UA，被闲鱼整站重定向到 passport 登录页。三组对照实验证明 UA 是闸门。
"""
import os

import pytest

from src.scraper import (
    DEFAULT_USER_AGENT,
    DESKTOP_VIEWPORT,
    MOBILE_VIEWPORT,
    _default_context_options,
    _looks_like_mobile,
)


@pytest.fixture(autouse=True)
def _clear_ua_env(monkeypatch):
    monkeypatch.delenv("BROWSER_USER_AGENT", raising=False)


def test_default_ua_is_desktop():
    """默认必须是桌面 UA —— 移动 Nexus 5 UA 会被闲鱼判为异常。"""
    opts = _default_context_options()
    assert opts["user_agent"] == DEFAULT_USER_AGENT
    assert "Nexus 5" not in opts["user_agent"]
    assert _looks_like_mobile(opts["user_agent"]) is False


def test_default_is_not_mobile():
    opts = _default_context_options()
    assert opts["is_mobile"] is False
    assert opts["has_touch"] is False
    assert opts["viewport"] == DESKTOP_VIEWPORT
    assert opts["device_scale_factor"] == 1


def test_mobile_ua_gets_mobile_viewport(monkeypatch):
    """显式指定移动 UA 时，视口/触摸必须跟着切到移动档（自洽）。"""
    mobile_ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    )
    monkeypatch.setenv("BROWSER_USER_AGENT", mobile_ua)
    opts = _default_context_options()
    assert opts["user_agent"] == mobile_ua
    assert opts["is_mobile"] is True
    assert opts["has_touch"] is True
    assert opts["viewport"] == MOBILE_VIEWPORT
    assert opts["device_scale_factor"] == 2.625


def test_env_override_desktop(monkeypatch):
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0 Safari/537.36"
    monkeypatch.setenv("BROWSER_USER_AGENT", ua)
    opts = _default_context_options()
    assert opts["user_agent"] == ua
    assert opts["is_mobile"] is False
    assert opts["viewport"] == DESKTOP_VIEWPORT


def test_env_override_strips_whitespace(monkeypatch):
    monkeypatch.setenv("BROWSER_USER_AGENT", "   " + DEFAULT_USER_AGENT + "  ")
    assert _default_context_options()["user_agent"] == DEFAULT_USER_AGENT


def test_locale_and_timezone_kept():
    opts = _default_context_options()
    assert opts["locale"] == "zh-CN"
    assert opts["timezone_id"] == "Asia/Shanghai"


def test_returned_viewports_are_copies():
    """调用方可能改 viewport，不能污染模块级常量。"""
    a = _default_context_options()
    a["viewport"]["width"] = 1
    assert _default_context_options()["viewport"] == DESKTOP_VIEWPORT
