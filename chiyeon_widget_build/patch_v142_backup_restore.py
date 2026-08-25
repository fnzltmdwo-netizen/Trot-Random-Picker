from pathlib import Path
import re

root=Path('.')
java=root/'app/src/main/java/com/mandarin/chiyeonwidget'
layout=root/'app/src/main/res/layout/activity_main.xml'
gradle=root/'app/build.gradle.kts'

(java/'BackupRestoreManager.java').write_text(r'''package com.mandarin.chiyeonwidget;

import android.content.Context;
import android.net.Uri;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

public final class BackupRestoreManager {
    private static final String META = "chiyeon_backup.json";
    private static final String MASTER = "gpt_master_conversation.txt";
    private BackupRestoreManager() {}

    public static final class RestoreResult {
        public final int masterChars;
        public final int contextItems;
        RestoreResult(int masterChars, int contextItems) {
            this.masterChars = masterChars;
            this.contextItems = contextItems;
        }
    }

    public static void exportTo(Context c, Uri uri) throws Exception {
        String master = GptMasterStore.read(c);
        JSONObject meta = Prefs.exportPortableState(c);
        meta.put("backup_format", 1);
        meta.put("master_chars", master.length());
        meta.put("created_at", System.currentTimeMillis());
        OutputStream raw = c.getContentResolver().openOutputStream(uri, "w");
        if (raw == null) throw new IllegalStateException("백업 파일을 열 수 없어.");
        try (OutputStream out = raw; ZipOutputStream zip = new ZipOutputStream(out)) {
            put(zip, META, meta.toString(2));
            put(zip, MASTER, master);
        }
    }

    public static RestoreResult restoreFrom(Context c, Uri uri) throws Exception {
        String metaText = null;
        String masterText = null;
        InputStream raw = c.getContentResolver().openInputStream(uri);
        if (raw == null) throw new IllegalStateException("백업 파일을 열 수 없어.");
        try (InputStream in = raw; ZipInputStream zip = new ZipInputStream(in)) {
            ZipEntry e;
            while ((e = zip.getNextEntry()) != null) {
                if (e.isDirectory()) continue;
                if (META.equals(e.getName())) metaText = readEntry(zip, 512_000);
                else if (MASTER.equals(e.getName())) masterText = readEntry(zip, 8_000_000);
            }
        }
        if (metaText == null) throw new IllegalArgumentException("치연 백업 정보가 없는 파일이야.");
        JSONObject meta = new JSONObject(metaText);
        if (meta.optInt("backup_format", 0) != 1) throw new IllegalArgumentException("지원하지 않는 치연 백업 형식이야.");
        if (masterText == null) masterText = "";
        int expected = meta.optInt("master_chars", masterText.length());
        if (expected > 1000 && masterText.length() < expected * 0.90) {
            throw new IllegalStateException("MASTER 내용이 일부 빠진 백업처럼 보여서 복원을 중단했어.");
        }
        GptMasterStore.save(c, masterText);
        Prefs.restorePortableState(c, meta);
        return new RestoreResult(masterText.length(), Prefs.contextItems(c));
    }

    private static void put(ZipOutputStream zip, String name, String text) throws Exception {
        zip.putNextEntry(new ZipEntry(name));
        zip.write((text == null ? "" : text).getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
    }

    private static String readEntry(ZipInputStream zip, int maxBytes) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n, total = 0;
        while ((n = zip.read(buf)) > 0) {
            total += n;
            if (total > maxBytes) throw new IllegalArgumentException("백업 파일 항목이 너무 커.");
            out.write(buf, 0, n);
        }
        return out.toString(StandardCharsets.UTF_8.name());
    }
}
''', encoding='utf-8')

p=java/'Prefs.java'
s=p.read_text('utf-8')
if 'import org.json.JSONObject;' not in s:
    s=s.replace('import android.content.SharedPreferences;','import android.content.SharedPreferences;\nimport org.json.JSONObject;')
insert='''\n    public static JSONObject exportPortableState(Context c) throws Exception {\n        JSONObject o = new JSONObject();\n        o.put("share_url", shareUrl(c));\n        o.put("style_profile", styleProfile(c));\n        o.put("user_context", userContext(c));\n        o.put("context_items", contextItems(c));\n        o.put("last_quote", quote(c));\n        o.put("source_chars", sourceChars(c));\n        o.put("analyzed_at", analyzedAt(c));\n        o.put("last_mood", lastMood(c));\n        o.put("visual_revision", visualRevision(c));\n        o.put("master_title", masterTitle(c));\n        o.put("master_turns", masterTurns(c));\n        o.put("master_first", masterFirst(c));\n        o.put("master_last", masterLast(c));\n        o.put("context_rotation", p(c).getInt(KEY_CONTEXT_ROTATION, 0));\n        return o;\n    }\n\n    public static void restorePortableState(Context c, JSONObject o) {\n        SharedPreferences.Editor e = p(c).edit();\n        e.putString(KEY_SHARE, o.optString("share_url", ""));\n        e.putString(KEY_STYLE, o.optString("style_profile", DefaultStyle.PROFILE));\n        e.putString(KEY_USER_CONTEXT, o.optString("user_context", ""));\n        e.putInt(KEY_CONTEXT_ITEMS, Math.max(0, Math.min(20, o.optInt("context_items", 0))));\n        e.putString(KEY_QUOTE, o.optString("last_quote", LocalComfortBank.defaultQuote()));\n        e.putInt(KEY_SOURCE_CHARS, Math.max(0, o.optInt("source_chars", 0)));\n        e.putLong(KEY_ANALYZED_AT, Math.max(0L, o.optLong("analyzed_at", 0L)));\n        e.putString(KEY_LAST_MOOD, o.optString("last_mood", ""));\n        e.putInt(KEY_VISUAL_REV, Math.max(0, o.optInt("visual_revision", 0)));\n        e.putString(KEY_MASTER_TITLE, o.optString("master_title", ""));\n        e.putInt(KEY_MASTER_TURNS, o.optInt("master_turns", 0));\n        e.putString(KEY_MASTER_FIRST, o.optString("master_first", ""));\n        e.putString(KEY_MASTER_LAST, o.optString("master_last", ""));\n        e.putInt(KEY_CONTEXT_ROTATION, Math.max(0, o.optInt("context_rotation", 0)));\n        e.putBoolean(KEY_MOBILE_CAPTURE_ACTIVE, false);\n        e.putBoolean(KEY_MOBILE_CAPTURE_READY, false);\n        e.putBoolean(KEY_IMPORTANCE_RUNNING, false);\n        e.putBoolean(KEY_IMPORTANCE_SUCCESS, true);\n        e.putString(KEY_IMPORTANCE_STATUS, "✅ 백업 파일에서 치연 데이터 복원 완료");\n        e.apply();\n    }\n'''
needle='\n    public static void saveSettings(Context c, String apiKey, String share) {'
if insert.strip() not in s:
    s=s.replace(needle, insert+needle)
p.write_text(s,'utf-8')

p=java/'MainActivity.java'
s=p.read_text('utf-8')
s=s.replace('private static final int REQ_EXPORT_ZIP = 1338;', 'private static final int REQ_EXPORT_ZIP = 1338;\n    private static final int REQ_BACKUP_CREATE = 1441;\n    private static final int REQ_BACKUP_RESTORE = 1442;')
s=s.replace('private Button rebuildImportanceButton;\n    private Button refreshButton;', 'private Button rebuildImportanceButton;\n    private Button backupButton;\n    private Button restoreButton;\n    private TextView backupStatus;\n    private Button refreshButton;')
s=s.replace('rebuildImportanceButton = findViewById(R.id.rebuild_importance_button);\n        refreshButton = findViewById(R.id.refresh_button);', 'rebuildImportanceButton = findViewById(R.id.rebuild_importance_button);\n        backupButton = findViewById(R.id.backup_button);\n        restoreButton = findViewById(R.id.restore_button);\n        backupStatus = findViewById(R.id.backup_status);\n        refreshButton = findViewById(R.id.refresh_button);')
s=s.replace('rebuildImportanceButton.setOnClickListener(v -> rebuildImportanceFromStoredMaster());\n        refreshButton.setOnClickListener(v -> refreshComfort());', 'rebuildImportanceButton.setOnClickListener(v -> rebuildImportanceFromStoredMaster());\n        backupButton.setOnClickListener(v -> createPortableBackup());\n        restoreButton.setOnClickListener(v -> choosePortableBackup());\n        refreshButton.setOnClickListener(v -> refreshComfort());')
methods='''
    private void createPortableBackup() {
        saveFields();
        Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/zip");
        String stamp = new java.text.SimpleDateFormat("yyyyMMdd_HHmm", Locale.KOREA).format(new java.util.Date());
        i.putExtra(Intent.EXTRA_TITLE, "ChiyeonBackup_" + stamp + ".chiyeonbak");
        startActivityForResult(i, REQ_BACKUP_CREATE);
    }

    private void choosePortableBackup() {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("*/*");
        startActivityForResult(i, REQ_BACKUP_RESTORE);
    }

    private void doPortableBackup(Uri uri) {
        setBusy(true, "MASTER + 중요 이야기 + 치연 설정을 백업 파일로 저장하는 중…");
        executor.execute(() -> {
            try {
                BackupRestoreManager.exportTo(this, uri);
                int chars = GptMasterStore.chars(this);
                runOnUiThread(() -> {
                    setBusy(false, "");
                    backupStatus.setText("✅ 백업 완료 · MASTER " + chars + "자 + 중요 이야기 " + Prefs.contextItems(this) + "개 저장됨\nAPI Key는 보안상 백업하지 않음");
                    updateStatus();
                    toast("치연 백업 파일 저장 완료!");
                });
            } catch (Exception e) {
                runOnUiThread(() -> { setBusy(false, ""); backupStatus.setText("⚠️ 백업 실패: " + friendlyError(e)); });
            }
        });
    }

    private void confirmPortableRestore(Uri uri) {
        new AlertDialog.Builder(this)
                .setTitle("치연 데이터 복원")
                .setMessage("현재 MASTER/중요 이야기/치연 설정을 선택한 백업으로 바꿀까?\n\nOpenAI API Key는 건드리지 않아.")
                .setPositiveButton("복원", (d, w) -> doPortableRestore(uri))
                .setNegativeButton("취소", null)
                .show();
    }

    private void doPortableRestore(Uri uri) {
        setBusy(true, "치연 백업에서 MASTER와 중요 이야기를 복원하는 중…");
        executor.execute(() -> {
            try {
                BackupRestoreManager.RestoreResult r = BackupRestoreManager.restoreFrom(this, uri);
                runOnUiThread(() -> {
                    shareUrl.setText(Prefs.shareUrl(this));
                    previewQuote.setText(Prefs.quote(this));
                    updatePreviewVisuals();
                    ChiyeonWidgetProvider.updateAll(this);
                    setBusy(false, "");
                    backupStatus.setText("✅ 복원 완료 · MASTER " + r.masterChars + "자 · 중요 이야기 " + r.contextItems + "개\nAPI Key만 필요하면 다시 입력하면 돼");
                    updateStatus();
                    toast("치연 데이터 복원 완료!");
                });
            } catch (Exception e) {
                runOnUiThread(() -> { setBusy(false, ""); backupStatus.setText("⚠️ 복원 실패: " + friendlyError(e)); });
            }
        });
    }

'''
needle='    private void openExportZip() {'
if 'private void createPortableBackup()' not in s:
    s=s.replace(needle, methods+needle)
needle='''        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQ_EXPORT_ZIP) {'''
rep='''        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQ_BACKUP_CREATE) {
            if (resultCode == RESULT_OK && data != null && data.getData() != null) doPortableBackup(data.getData());
            return;
        }
        if (requestCode == REQ_BACKUP_RESTORE) {
            if (resultCode == RESULT_OK && data != null && data.getData() != null) confirmPortableRestore(data.getData());
            return;
        }

        if (requestCode == REQ_EXPORT_ZIP) {'''
s=s.replace(needle,rep)
s=s.replace('rebuildImportanceButton.setEnabled(!busy);\n        refreshButton.setEnabled(!busy);', 'rebuildImportanceButton.setEnabled(!busy);\n        backupButton.setEnabled(!busy);\n        restoreButton.setEnabled(!busy);\n        refreshButton.setEnabled(!busy);')
p.write_text(s,'utf-8')

p=layout
x=p.read_text('utf-8')
card='''
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="14dp"
            android:background="@drawable/card"
            android:orientation="vertical"
            android:padding="16dp">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="📦 백업 / 복원" android:textColor="#571028" android:textSize="18sp" android:textStyle="bold" />
            <TextView android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="5dp" android:text="MASTER · 중요 이야기 TOP8 · 치연 말투/대사 · 위젯 상태를 파일 하나로 저장해. API Key는 보안상 제외해." android:textColor="#7D6D73" android:textSize="12sp" />
            <Button android:id="@+id/backup_button" android:layout_width="match_parent" android:layout_height="54dp" android:layout_marginTop="12dp" android:background="@drawable/button_primary" android:text="📤 내 치연 데이터 백업하기" android:textAllCaps="false" android:textColor="#FFFFFF" android:textStyle="bold" />
            <Button android:id="@+id/restore_button" android:layout_width="match_parent" android:layout_height="54dp" android:layout_marginTop="9dp" android:background="@drawable/button_primary" android:text="📥 치연 데이터 복원하기" android:textAllCaps="false" android:textColor="#FFFFFF" android:textStyle="bold" />
            <TextView android:id="@+id/backup_status" android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="9dp" android:text="폰 파일앱에 .chiyeonbak 파일로 저장/복원할 수 있어." android:textColor="#8A747B" android:textSize="11sp" />
        </LinearLayout>
'''
needle='''
        <Button
            android:id="@+id/refresh_button"'''
if '@+id/backup_button' not in x:
    x=x.replace(needle,card+needle)
p.write_text(x,'utf-8')

g=gradle.read_text('utf-8')
g=re.sub(r'versionCode\s*=\s*\d+', 'versionCode = 19', g)
g=re.sub(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.4.2"', g)
g=g.replace('ChiyeonComfortWidget-v1.4.1-debug.apks','ChiyeonComfortWidget-v1.4.2-debug.apks')
g=g.replace('"version_code":18','"version_code":19')
g=g.replace('"version_name":"1.4.1"','"version_name":"1.4.2"')
gradle.write_text(g,'utf-8')
print('patched v1.4.2 backup/restore')
