package com.chiyeon.overlay;

import android.accessibilityservice.AccessibilityService;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.provider.Settings;
import android.view.Gravity;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ChiyeonAccessibilityService extends AccessibilityService {
    private WindowManager wm;
    private LinearLayout overlay;
    private boolean visible = false;

    private final Set<String> targets = new HashSet<>(Arrays.asList(
        "com.realbyteapps.moneymanager",
        "com.realbyteapps.moneymanagerfree",
        "com.realbyte.money"
    ));

    private int dp(float v){ return (int)(v * getResources().getDisplayMetrics().density + 0.5f); }

    @Override public void onServiceConnected() {
        super.onServiceConnected();
        wm = (WindowManager)getSystemService(WINDOW_SERVICE);
        buildOverlay();
    }

    private void buildOverlay(){
        overlay = new LinearLayout(this);
        overlay.setOrientation(LinearLayout.HORIZONTAL);
        overlay.setGravity(Gravity.CENTER_VERTICAL);
        overlay.setPadding(dp(12), dp(7), dp(12), dp(7));
        overlay.setBackgroundResource(R.drawable.overlay_card);

        TextView t = new TextView(this);
        t.setText("이번 달도 카드가 먼저 신났네? 👀");
        t.setTextSize(14);
        t.setTextColor(Color.rgb(85,42,60));
        t.setGravity(Gravity.CENTER_VERTICAL);
        LinearLayout.LayoutParams tp = new LinearLayout.LayoutParams(0, -2, 1f);
        overlay.addView(t, tp);

        ImageView img = new ImageView(this);
        img.setImageResource(R.drawable.chiyeon);
        img.setScaleType(ImageView.ScaleType.CENTER_INSIDE);
        overlay.addView(img, new LinearLayout.LayoutParams(dp(72), dp(82)));
    }

    private WindowManager.LayoutParams params(){
        WindowManager.LayoutParams p = new WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            dp(98),
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE |
                WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT
        );
        p.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
        p.x = 0;
        p.y = dp(145);
        return p;
    }

    private void show(){
        if (visible || overlay == null || !Settings.canDrawOverlays(this)) return;
        try {
            wm.addView(overlay, params());
            visible = true;
        } catch (Exception ignored) {}
    }

    private void hide(){
        if (!visible || overlay == null) return;
        try { wm.removeView(overlay); } catch (Exception ignored) {}
        visible = false;
    }

    @Override public void onAccessibilityEvent(AccessibilityEvent event) {
        CharSequence pkg = event.getPackageName();
        if (pkg == null) return;
        if (targets.contains(pkg.toString())) show();
        else if (!pkg.toString().equals(getPackageName())) hide();
    }

    @Override public void onInterrupt() { hide(); }
    @Override public void onDestroy() { hide(); super.onDestroy(); }
}
