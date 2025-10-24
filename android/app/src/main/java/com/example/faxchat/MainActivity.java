package com.example.faxchat;

import android.os.Bundle;
import android.webkit.WebView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

	private WebView webView;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		getSupportActionBar().hide();
		setContentView(R.layout.activity_main);

		webView = findViewById(R.id.webView); // Make sure you have a WebView element in your activity's layout XML.

		// Enable JavaScript (optional, if your HTML file uses JavaScript)
		webView.getSettings().setJavaScriptEnabled(true);

		// Load the local HTML file from the assets folder
		webView.loadUrl("file:///android_asset/index.html");
	}
}
