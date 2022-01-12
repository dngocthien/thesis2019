package com.tttv.thiendinh.breakroid;

import android.content.Intent;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.tttv.thiendinh.breakroid.Model.Room;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class MainActivity extends AppCompatActivity {
    private long backPressedTime;
    public static final String KEY_ROOM = "keyRoom";
    public static final String KEY_SOUND = "keySound";
    public static final String EXTRA_ID = "EXTRA_ID";
    private int state = 0;
    FirebaseDatabase database;
    DatabaseReference myRef;

    private EditText txt_id, txt_pw;
    private Button btn_subscribe;
    private Room room;

    public int getState() {
        return state;
    }

    public void setState(int state) {
        this.state = state;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        state = 1;

        String savedId = PreferenceManager.getDefaultSharedPreferences(this).getString(KEY_ROOM, "nothing+");

        if (!savedId.equals("nothing+")){
            goHome(savedId);
        }

        txt_id = findViewById(R.id.id);
        txt_pw = findViewById(R.id.pw);
        btn_subscribe = findViewById(R.id.subscribe);
        btn_subscribe.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                subs();
            }
        });
    }

    private void subs() {
        final String id = txt_id.getText().toString().trim();
        final String pw = txt_pw.getText().toString().trim();
        if (id.equals("")) {
            toast("Please add id!");
            return;
        }
        if (pw.equals("")) {
            toast("Please add password!");
            return;
        }
        database = FirebaseDatabase.getInstance();
        myRef = database.getReference("room/" + id);
        myRef.addListenerForSingleValueEvent(new ValueEventListener() {

            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                if(dataSnapshot.exists()) {
                    room = dataSnapshot.getValue(Room.class);
                    if(md5(pw).equals(room.getPw())) {
                        goHome(id);
                        toast("Registered successfully!");
                    }
                    else {
                        txt_pw.setText("");
                        toast("Password is wrong!");
                    }
                }
                else toast("This id does not exist!");
            }

            @Override
            public void onCancelled(DatabaseError error) {
                toast("Updating is canceled!");
            }
        });
    }

    private void goHome(String id) {
        Intent intent = new Intent(this, HomeActivity.class);
        intent.putExtra(EXTRA_ID, id);
        startActivity(intent);
        finish();
    }

    @Override
    public void onBackPressed() {
        if (backPressedTime + 2000 > System.currentTimeMillis())
            super.onBackPressed();
        else toast("Press Back again to exist");
        backPressedTime = System.currentTimeMillis();
    }

    private void toast(String text) {
        Toast.makeText(MainActivity.this, text, Toast.LENGTH_LONG).show();
    }

    public static final String md5(final String s) {
        final String MD5 = "MD5";
        try {
            // Create MD5 Hash
            MessageDigest digest = java.security.MessageDigest.getInstance(MD5);
            digest.update(s.getBytes());
            byte messageDigest[] = digest.digest();

            // Create Hex String
            StringBuilder hexString = new StringBuilder();
            for (byte aMessageDigest : messageDigest) {
                String h = Integer.toHexString(0xFF & aMessageDigest);
                while (h.length() < 2)
                    h = "0" + h;
                hexString.append(h);
            }
            return hexString.toString();

        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
        return "";
    }

}
