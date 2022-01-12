package com.tttv.thiendinh.breakroid.adapter;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import com.squareup.picasso.Picasso;
import com.tttv.thiendinh.breakroid.R;

import java.util.ArrayList;

public class SoundListViewAdapter extends ArrayAdapter<String>{

    private ArrayList<String> dataSet;
    private ArrayList<Integer> lenghSet;
    private Context mContext;
    private int selected;

    private static class ViewHolder {
        private TextView txt_left, txt_right;
        private ImageView img_avatar;
    }

    public SoundListViewAdapter(ArrayList<String> data, ArrayList<Integer> length, Context context, int setected) {
        super(context, R.layout.row_item, data);
        this.dataSet = data;
        this.lenghSet = length;
        this.mContext = context;
        this.selected = setected;
    }

    private int lastPosition = -1;

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        // Check if an existing view is being reused, otherwise inflate the view
        ViewHolder viewHolder; // view lookup cache stored in tag

        final View result;

        if (convertView == null) {

            viewHolder = new ViewHolder();
            LayoutInflater inflater = LayoutInflater.from(getContext());
            convertView = inflater.inflate(R.layout.row_item, parent, false);
            viewHolder.txt_left = (TextView) convertView.findViewById(R.id.item_title);
            viewHolder.txt_right = (TextView) convertView.findViewById(R.id.item_length);
            viewHolder.img_avatar = (ImageView) convertView.findViewById(R.id.img_avatar);

            result = convertView;

            convertView.setTag(viewHolder);
        } else {
            viewHolder = (ViewHolder) convertView.getTag();
            result = convertView;
        }

        Animation animation = AnimationUtils.loadAnimation(mContext, (position > lastPosition) ? R.anim.top_down : R.anim.bottom_up);
        result.startAnimation(animation);
        lastPosition = position;

        if(position==this.selected) {
            Picasso.get().load(R.drawable.sound2).into(viewHolder.img_avatar);
        }
        viewHolder.txt_left.setText(dataSet.get(position));
        viewHolder.txt_right.setText(formatDuration(lenghSet.get(position)));
        return convertView;
    }

    public static String formatDuration(int duration) {
        String positive = String.format(
                "%d:%02d:%02d",
                duration / 3600,
                (duration % 3600) / 60,
                duration % 60);
        return positive;
    }
}