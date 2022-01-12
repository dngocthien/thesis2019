package com.tttv.thiendinh.breakroid;

import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import com.tttv.thiendinh.breakroid.adapter.SoundListViewAdapter;

import java.util.ArrayList;
import java.util.Arrays;

public class SoundActivity extends AppCompatActivity {
    private ArrayList<String> soundList;
    private ArrayList<Integer> lengthList;
    private ListView listview_sound;
    private long pressedTime;
    private int pressedPosition;
    private Ringtone r;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sound);

        int selected = PreferenceManager.getDefaultSharedPreferences(this).getInt(MainActivity.KEY_SOUND, 0);

        soundList = new ArrayList<>();
        soundList.add("Alarm");
        soundList.add("Alarm 2");
        soundList.add("Beep");
        soundList.add("Bird");
        soundList.add("Cartoon");
        soundList.add("Fast");
        soundList.add("Pig");
        soundList.add("SOS");
        lengthList = new ArrayList<Integer>(Arrays.asList(7, 5, 4, 4, 5, 1, 2, 10));

        listview_sound = (ListView) findViewById(R.id.listview_ranking);

        ArrayAdapter adapter = new SoundListViewAdapter(soundList, lengthList, this, selected);
        listview_sound.setAdapter(adapter);
        listview_sound.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                if (pressedTime + 2000 > System.currentTimeMillis() && pressedPosition == position) {
                    saveSound(position);
                }
                else{
                    if(r != null && r.isPlaying())
                        r.stop();
                    playSound(position);
                }
                pressedTime = System.currentTimeMillis();
                pressedPosition = position;
            }
        });
    }

    private void toast(String text) {
        Toast.makeText(this, text, Toast.LENGTH_LONG).show();
    }

    private void playSound(int position){
        try {
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
            r = RingtoneManager.getRingtone(getApplicationContext(), sound);
            r.play();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void saveSound(int saved) {
        PreferenceManager.getDefaultSharedPreferences(this).edit().putInt(MainActivity.KEY_SOUND, saved).apply();
        toast("Sound changed successfully!");
        onBackPressed();
    }
}
