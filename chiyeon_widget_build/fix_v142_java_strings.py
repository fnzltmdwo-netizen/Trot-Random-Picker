from pathlib import Path

p = Path('app/src/main/java/com/mandarin/chiyeonwidget/MainActivity.java')
s = p.read_text('utf-8')

s = s.replace(
    'backupStatus.setText("✅ 백업 완료 · MASTER " + chars + "자 + 중요 이야기 " + Prefs.contextItems(this) + "개 저장됨\nAPI Key는 보안상 백업하지 않음");',
    'backupStatus.setText("✅ 백업 완료 · MASTER " + chars + "자 + 중요 이야기 " + Prefs.contextItems(this) + "개 저장됨\\nAPI Key는 보안상 백업하지 않음");'
)

s = s.replace(
    '.setMessage("현재 MASTER/중요 이야기/치연 설정을 선택한 백업으로 바꿀까?\n\nOpenAI API Key는 건드리지 않아.")',
    '.setMessage("현재 MASTER/중요 이야기/치연 설정을 선택한 백업으로 바꿀까?\\n\\nOpenAI API Key는 건드리지 않아.")'
)

s = s.replace(
    'backupStatus.setText("✅ 복원 완료 · MASTER " + r.masterChars + "자 · 중요 이야기 " + r.contextItems + "개\nAPI Key만 필요하면 다시 입력하면 돼");',
    'backupStatus.setText("✅ 복원 완료 · MASTER " + r.masterChars + "자 · 중요 이야기 " + r.contextItems + "개\\nAPI Key만 필요하면 다시 입력하면 돼");'
)

p.write_text(s, 'utf-8')

# Fail fast if a raw newline still sits inside one of the three Java literals.
checks = [
    '개 저장됨\\nAPI Key는 보안상 백업하지 않음',
    '바꿀까?\\n\\nOpenAI API Key는 건드리지 않아.',
    '개\\nAPI Key만 필요하면 다시 입력하면 돼',
]
for item in checks:
    if item not in s:
        raise SystemExit('v1.4.2 string repair failed: ' + item)

print('v1.4.2 Java string literals repaired')
