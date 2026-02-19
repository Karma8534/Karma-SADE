"""
Karma SMS — Twilio-powered notifications + two-way chat.

Outbound: Karma sends breakthrough insights, alerts, and discoveries via SMS.
Inbound: Colby can text back to chat with Karma from anywhere.

Throttle: max 3/hr, 10/day, confidence >= 0.8
Two-way: unlimited when user initiates via SMS.
"""
import asyncio
import json
import time
from collections import deque
from datetime import datetime, timezone
from typing import Optional

import config

# ─── SMS Categories (triggers for outbound) ────────────────────────────────
SMS_CATEGORIES = {
    "breakthrough_insight",     # Novel connection across conversations
    "problem_prevention",       # Alert about potential issues
    "cross_platform_synthesis", # Pattern spanning multiple AI platforms
    "timing_sensitive",         # Time-relevant information
    "self_improvement",         # Karma's own growth milestones
}

# ─── Throttle Config ────────────────────────────────────────────────────────
MAX_PER_HOUR = 3
MAX_PER_DAY = 10
MIN_CONFIDENCE = 0.8


class SMSManager:
    """Manages Twilio SMS for Karma — outbound notifications + inbound chat."""

    def __init__(self, generate_response_fn=None):
        self._client = None
        self._from_number = None
        self._to_number = config.SMS_TO_NUMBER
        self._generate_response = generate_response_fn  # For two-way chat

        # Throttle state
        self._send_times_hour: deque = deque()  # timestamps of sends in current hour
        self._send_times_day: deque = deque()    # timestamps of sends in current day
        self._total_sent = 0
        self._total_blocked = 0

        # Initialize Twilio client
        self._init_client()

    def _init_client(self):
        """Initialize Twilio client from env vars."""
        sid = config.TWILIO_ACCOUNT_SID
        token = config.TWILIO_AUTH_TOKEN
        from_num = config.TWILIO_FROM_NUMBER

        if not all([sid, token, from_num]):
            print("[SMS] Twilio credentials missing — SMS disabled")
            print(f"[SMS]   SID: {'set' if sid else 'MISSING'}")
            print(f"[SMS]   Token: {'set' if token else 'MISSING'}")
            print(f"[SMS]   From: {'set' if from_num else 'MISSING'}")
            return

        try:
            from twilio.rest import Client
            self._client = Client(sid, token)
            self._from_number = from_num
            print(f"[SMS] Twilio initialized — from {from_num} → {self._to_number}")
        except ImportError:
            print("[SMS] twilio package not installed — SMS disabled")
        except Exception as e:
            print(f"[SMS] Twilio init failed: {e}")

    @property
    def enabled(self) -> bool:
        return self._client is not None and self._from_number is not None

    def _check_throttle(self) -> tuple[bool, str]:
        """Check if we can send (throttle limits). Returns (allowed, reason)."""
        now = time.time()

        # Prune old entries
        hour_ago = now - 3600
        while self._send_times_hour and self._send_times_hour[0] < hour_ago:
            self._send_times_hour.popleft()

        day_ago = now - 86400
        while self._send_times_day and self._send_times_day[0] < day_ago:
            self._send_times_day.popleft()

        if len(self._send_times_hour) >= MAX_PER_HOUR:
            return False, f"Hourly limit ({MAX_PER_HOUR}/hr)"
        if len(self._send_times_day) >= MAX_PER_DAY:
            return False, f"Daily limit ({MAX_PER_DAY}/day)"

        return True, "OK"

    def _record_send(self):
        """Record a successful send for throttle tracking."""
        now = time.time()
        self._send_times_hour.append(now)
        self._send_times_day.append(now)
        self._total_sent += 1

    async def notify(self, message: str, category: str = "breakthrough_insight",
                     confidence: float = 0.8) -> bool:
        """Send an outbound SMS notification. Returns True if sent."""
        if not self.enabled:
            return False

        # Validate category
        if category not in SMS_CATEGORIES:
            print(f"[SMS] Unknown category: {category}")
            return False

        # Check confidence threshold
        if confidence < MIN_CONFIDENCE:
            self._total_blocked += 1
            return False

        # Check throttle
        allowed, reason = self._check_throttle()
        if not allowed:
            self._total_blocked += 1
            print(f"[SMS] Throttled: {reason}")
            return False

        # Format message with Karma branding
        ts = datetime.now(timezone.utc).strftime("%H:%M UTC")
        sms_body = f"[Karma {ts}] {message}"

        # Truncate to SMS limit (1600 chars for long SMS)
        if len(sms_body) > 1600:
            sms_body = sms_body[:1597] + "..."

        try:
            self._client.messages.create(
                body=sms_body,
                from_=self._from_number,
                to=self._to_number,
            )
            self._record_send()
            print(f"[SMS] Sent ({category}, conf={confidence:.1f}): {message[:60]}...")
            return True
        except Exception as e:
            print(f"[SMS] Send failed: {e}")
            return False

    async def handle_inbound(self, from_number: str, body: str) -> str:
        """Handle an inbound SMS — unlimited two-way chat when user initiates."""
        if from_number != self._to_number:
            print(f"[SMS] Ignoring message from unknown number: {from_number}")
            return ""

        print(f"[SMS] Inbound from Colby: {body[:60]}...")

        # Generate response via Karma's chat engine
        if self._generate_response:
            try:
                from server import ConversationManager
                conversation = ConversationManager(max_history=4)
                reply, model_used = await self._generate_response(body, conversation)

                # Log to ledger
                from server import log_to_ledger
                log_to_ledger(body, reply, model_used=model_used)

                return reply
            except Exception as e:
                print(f"[SMS] Response generation failed: {e}")
                return "Karma here — having trouble thinking right now. Try again in a moment."
        else:
            return "Karma here — chat engine not connected. Use terminal for full conversations."

    def get_stats(self) -> dict:
        """Return SMS stats for /status endpoint."""
        now = time.time()
        hour_ago = now - 3600
        day_ago = now - 86400

        # Count active throttle windows
        recent_hour = sum(1 for t in self._send_times_hour if t > hour_ago)
        recent_day = sum(1 for t in self._send_times_day if t > day_ago)

        return {
            "enabled": self.enabled,
            "total_sent": self._total_sent,
            "total_blocked": self._total_blocked,
            "sent_last_hour": recent_hour,
            "sent_last_day": recent_day,
            "remaining_hour": MAX_PER_HOUR - recent_hour,
            "remaining_day": MAX_PER_DAY - recent_day,
            "to_number": self._to_number[-4:] if self._to_number else None,  # Last 4 digits only
        }
