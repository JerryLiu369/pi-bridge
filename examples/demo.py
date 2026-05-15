#!/usr/bin/env python3
"""
Quick demo: call the local Pi agent and print the response.
Uses the ANTHROPIC_API_KEY environment variable.
"""

import os
import sys

# Add parent directory to path so pi_bridge can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pi_bridge import PiSession, Provider, Model, CustomTool

API_KEY = "$DEEPSEEK_API_KEY_PLACEHOLDER"

print("Initializing Pi session...")
session = PiSession(
    provider=Provider(
        base_url="https://api.deepseek.com/v1",
        api_key=API_KEY,
    ),
    model=Model(
        name="deepseek-chat",
        api_format="completion",
    ),
    tools=[],  # Disable built-in tools for this simple test
)

def print_events(events):
    for event in events:
        if event.type == "text_delta":
            print(event.delta, end="", flush=True)
        elif event.type == "agent_end":
            print(f"\n[stop_reason={event.stop_reason}]")
        elif event.type == "error":
            print(f"\n[ERROR: {event.message}]", file=sys.stderr)


# 第一轮
print("=== 第一轮 ===")
print_events(session.send("请给我一个1到10之间的随机数，只回答数字。"))

# 第二轮：不传历史，Pi 自己记得上一轮的内容
print("\n=== 第二轮（同一 session，Pi 记得上一轮的回答）===")
print_events(session.send("把你刚才说的那个数字乘以3，只回答结果。"))

print("\n=== 消息历史（共两轮）===")
for msg in session.messages:
    role = msg.get("role", "?")
    if role == "assistant":
        texts = [c["text"] for c in msg.get("content", []) if c.get("type") == "text"]
        print(f"assistant: {''.join(texts).strip()}")
    elif role == "user":
        print(f"user: {str(msg.get('content', '')).strip()}")

session.close()
print("\nDemo complete!")
