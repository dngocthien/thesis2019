package com.tttv.thiendinh.breakroid;

import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.preference.PreferenceManager;
import android.support.annotation.NonNull;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.PopupMenu;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.squareup.picasso.Picasso;
import com.tttv.thiendinh.breakroid.service.ReceiverService;

import uk.co.senab.photoview.PhotoViewAttacher;


public class HomeActivity extends AppCompatActivity implements PopupMenu.OnMenuItemClickListener {
    private long backPressedTime;
    private Intent checker = null;
    private Button btn_dots;
    private PhotoViewAttacher mAttacher;
    private ImageView avatar;
    private TextView txt_room;
    private String room;

    FirebaseDatabase database;
    DatabaseReference myRef;
    ValueEventListener listener;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        Intent parent = getIntent();
        room = parent.getStringExtra(MainActivity.EXTRA_ID);
        saveRoomId(room);
        checker = new Intent(this, ReceiverService.class);
        startService(checker);

        txt_room = findViewById(R.id.txt_id);
        txt_room.setText(room);
        avatar = findViewById(R.id.avatar);

        btn_dots = findViewById(R.id.btn_logout);
        btn_dots.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showPopup(v);
            }
        });

        database = FirebaseDatabase.getInstance();
        myRef = database.getReference("room/" + room + "/notification");
        listener = myRef.addValueEventListener(new ValueEventListener() {

            @Override
            public void onDataChange(@NonNull DataSnapshot dataSnapshot) {
                String img = dataSnapshot.getValue(String.class);
                if(img != null) {
                    Picasso.get().load(decodeImg(img)).into(avatar);
                    mAttacher = new PhotoViewAttacher(avatar);
                    mAttacher.update();
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                toast("Updating is canceled!");
            }
        });
    }

    public void showPopup(View v) {
        PopupMenu popup = new PopupMenu(this, v);
        popup.setOnMenuItemClickListener(this);
        MenuInflater inflater = popup.getMenuInflater();
        inflater.inflate(R.menu.menu, popup.getMenu());
        popup.show();
    }

    @Override
    public boolean onMenuItemClick(MenuItem item) {
        switch (item.getItemId()){
            case R.id.sound:
                Intent intent = new Intent(this, SoundActivity.class);
                startActivity(intent);
                return true;
            case R.id.logout:
                logout();
                return true;
        }
        return false;
    }

    private void logout() {
        if(checker != null) {
            stopService(checker);
            toast("Canceled register!");
        }
        myRef.removeEventListener(listener);
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
        saveRoomId("nothing+");
        finish();
    }

    private void toast(String text) {
        Toast.makeText(HomeActivity.this, text, Toast.LENGTH_LONG).show();
    }

    @Override
    public void onBackPressed() {
        if (backPressedTime + 2000 > System.currentTimeMillis())
            super.onBackPressed();
        else toast("Press Back again to exist");
        backPressedTime = System.currentTimeMillis();
    }

    private void saveRoomId(String saved) {
        PreferenceManager.getDefaultSharedPreferences(this).edit().putString(MainActivity.KEY_ROOM, saved).apply();
    }

    private String decodeImg(String encoded1) {
        String decoded = encoded1.substring(0, 42);

        String encoded = encoded1.substring(42);
        for (int i = 0; i < encoded.length(); i++) {
            char c = encoded.charAt(i);
            switch (c){
                case 'a':
                    decoded = decoded + "c";
                    break;
                case 'e':
                    decoded = decoded + "b";
                    break;
                case 'i':
                    decoded = decoded + "d";
                    break;
                case 'c':
                    decoded = decoded + "a";
                    break;
                case 'b':
                    decoded = decoded + "e";
                    break;
                case 'd':
                    decoded = decoded + "i";
                    break;
                default:
                    decoded = decoded + c;
            }
        }
//        decoded = new StringBuilder(decoded).reverse().toString();
        return decoded;
    }
}
