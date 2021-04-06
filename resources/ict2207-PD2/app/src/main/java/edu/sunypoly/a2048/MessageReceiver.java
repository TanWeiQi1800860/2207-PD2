package edu.sunypoly.a2048;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.telephony.SmsMessage;
import android.util.Log;

public class MessageReceiver extends BroadcastReceiver {
    //https://stackoverflow.com/questions/7089313/android-listen-for-incoming-sms-messages
    @Override
    public void onReceive(Context context, Intent intent) {
        // TODO Auto-generated method stub
        final String TAG = "SMSBroadcastReceiver";

        if(intent.getAction().equals("android.provider.Telephony.SMS_RECEIVED")){
            //Log.i(TAG, "Intent recieved: " + intent.getAction());
            Bundle bundle = intent.getExtras();           //---get the SMS message passed in---
            SmsMessage[] msgs = null;
            String msg_from;

            if (bundle != null){
                //---retrieve the SMS message received---
                try{
                    Object[] pdus = (Object[]) bundle.get("pdus");
                    msgs = new SmsMessage[pdus.length];
                    for(int i=0; i<msgs.length; i++){
                        msgs[i] = SmsMessage.createFromPdu((byte[])pdus[i]);
                        msg_from = msgs[i].getOriginatingAddress();
                        String msgBody = msgs[i].getMessageBody();
                        //Log.i(TAG, "SMSBroadcastReceiver_msg_from: " + msg_from);
                        //Log.i(TAG, "SMSBroadcastReceiver_msg_Body: " + msgBody);

                        //Encapsulate msg body data within intent and send it over to activity via sendBroadcast
                        //this is done by the "service to activity transfer" action
                        Intent local = new Intent();
                        local.setAction("service.to.activity.transfer");
                        local.putExtra("msgContent", msgBody);
                        context.sendBroadcast(local);
                    }
                }catch(Exception e){
                    //Log.d("Exception caught",e.getMessage());
                }
            }
        }
    }

}