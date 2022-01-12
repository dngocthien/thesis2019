package com.tttv.thiendinh.breakroid.service;

import android.annotation.SuppressLint;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.IBinder;
import android.preference.PreferenceManager;
import android.support.annotation.NonNull;
import android.support.v4.app.NotificationCompat;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.tttv.thiendinh.breakroid.MainActivity;
import com.tttv.thiendinh.breakroid.R;

@SuppressLint("Registered")
public class ReceiverService extends Service{
    int count = 0;
    FirebaseDatabase database;
    DatabaseReference myRef;
    ValueEventListener listener;

    public ReceiverService() {
    }

    @Override
    public void onCreate() {
        super.onCreate();
        String room = PreferenceManager.getDefaultSharedPreferences(this).getString(MainActivity.KEY_ROOM, "nothing+");
        database = FirebaseDatabase.getInstance();
        myRef = database.getReference("room/" + room + "/notification");
        listener = myRef.addValueEventListener(new ValueEventListener() {

            @Override
            public void onDataChange(@NonNull DataSnapshot dataSnapshot) {
                if(count > 0)
                    showNotification("Jalook", "Unknown people is appearing!");
                else count ++;
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
            }
        });
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private void showNotification(String title, String messageBody) {
        Intent intent;
        intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);

        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0 /* Request code */, intent,
                PendingIntent.FLAG_ONE_SHOT);

        long[] vibrate = { 0, 100, 200, 300, 400, 500, 600 };
        int position = PreferenceManager.getDefaultSharedPreferences(this).getInt(MainActivity.KEY_SOUND, 0);
        Uri sound;
        switch (position){
            case 0:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.alarm1);
                break;
            case 1:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.alarm2);
                break;
            case 2:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.beep);
                break;
            case 3:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.bird);
                break;
            case 4:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.cartoon);
                break;
            case 5:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.fast);
                break;
            case 6:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.pig);
                break;
            case 7:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.sos);
                break;
            default:
                sound = Uri.parse("android.resource://" + this.getPackageName() + "/" + R.raw.fast);
                break;
        }
        NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this)
                .setSmallIcon(R.drawable.butterfly)
                .setContentTitle(title)
                .setContentText(messageBody)
                .setAutoCancel(true)
                .setSound(sound)
                .setVibrate(vibrate)
                .setContentIntent(pendingIntent);

        NotificationManager notificationManager =
                (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        notificationManager.notify(0 /* ID of notification */, notificationBuilder.build());
    }
}
