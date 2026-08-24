package com.chiyeon.overlay;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private int dp(float v){ return (int)(v * getResources().getDisplayMetrics().density + 0.5f); }

    @Override public void onCreate(Bundle b){
        super.onCreate(b);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(24), dp(42), dp(24), dp(24));
        root.setGravity(Gravity.CENTER_HORIZONTAL);
        root.setBackgroundColor(Color.rgb(255,250,252));

        TextView title = new TextView(this);
        title.setText("치연 오버레이 우회앱 💸");
        title.setTextSize(25);
        title.setTextColor(Color.rgb(65,35,48));
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, -2));

        TextView info = new TextView(this);
        info.setText("\n원본 머니매니저는 건드리지 않고,\n앱이 켜질 때만 치연을 화면 위에 띄워요.\n\n① 다른 앱 위에 표시 허용\n② 접근성 서비스에서 ‘치연 오버레이’ 켜기");
        info.setTextSize(16);
        info.setTextColor(Color.DKGRAY);
        info.setGravity(Gravity.CENTER);
        root.addView(info, new LinearLayout.LayoutParams(-1, -2));

        Button overlay = new Button(this);
        overlay.setText("① 오버레이 권한 열기");
        overlay.setOnClickListener(v -> {
            Intent i = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:" + getPackageName()));
            startActivity(i);
        });
        LinearLayout.LayoutParams bp = new LinearLayout.LayoutParams(-1, dp(58));
        bp.topMargin = dp(28);
        root.addView(overlay, bp);

        Button access = new Button(this);
        access.setText("② 접근성 설정 열기");
        access.setOnClickListener(v -> startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)));
        LinearLayout.LayoutParams bp2 = new LinearLayout.LayoutParams(-1, dp(58));
        bp2.topMargin = dp(12);
        root.addView(access, bp2);

        TextView note = new TextView(this);
        note.setText("\n기본 감지 대상:\n• com.realbyteapps.moneymanager\n• com.realbyteapps.moneymanagerfree\n• com.realbyte.money\n\n다른 앱에서는 자동으로 사라집니다.");
        note.setTextSize(13);
        note.setTextColor(Color.GRAY);
        note.setGravity(Gravity.CENTER);
        root.addView(note, new LinearLayout.LayoutParams(-1, -2));

        setContentView(root);
    }
}
