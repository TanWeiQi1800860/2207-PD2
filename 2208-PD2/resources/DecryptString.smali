.class public Lcom/decryptmanager/DecryptString;
.super Ljava/lang/Object;
.source "DecryptString.java"


# static fields
.field private static key:[B

.field private static secret:Ljava/lang/String;

.field private static secretKey:Ljavax/crypto/spec/SecretKeySpec;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .line 16
    const-string v0, "Thereisnospoon"

    sput-object v0, Lcom/example/helloworld/DecryptString;->secret:Ljava/lang/String;

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 12
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static decrypt(Ljava/lang/String;)Ljava/lang/String;
    .locals 4
    .param p0, "strToDecrypt"    # Ljava/lang/String;

    .line 40
    :try_start_0
    sget-object v0, Lcom/example/helloworld/DecryptString;->secret:Ljava/lang/String;

    invoke-static {v0}, Lcom/example/helloworld/DecryptString;->setKey(Ljava/lang/String;)V

    .line 41
    const-string v0, "AES/ECB/PKCS5PADDING"

    invoke-static {v0}, Ljavax/crypto/Cipher;->getInstance(Ljava/lang/String;)Ljavax/crypto/Cipher;

    move-result-object v0

    .line 42
    .local v0, "cipher":Ljavax/crypto/Cipher;
    const/4 v1, 0x2

    sget-object v2, Lcom/example/helloworld/DecryptString;->secretKey:Ljavax/crypto/spec/SecretKeySpec;

    invoke-virtual {v0, v1, v2}, Ljavax/crypto/Cipher;->init(ILjava/security/Key;)V

    .line 43
    new-instance v1, Ljava/lang/String;

    invoke-static {}, Ljava/util/Base64;->getDecoder()Ljava/util/Base64$Decoder;

    move-result-object v2

    invoke-virtual {v2, p0}, Ljava/util/Base64$Decoder;->decode(Ljava/lang/String;)[B

    move-result-object v2

    invoke-virtual {v0, v2}, Ljavax/crypto/Cipher;->doFinal([B)[B

    move-result-object v2

    invoke-direct {v1, v2}, Ljava/lang/String;-><init>([B)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    return-object v1

    .line 45
    .end local v0    # "cipher":Ljavax/crypto/Cipher;
    :catch_0
    move-exception v0

    .line 47
    .local v0, "e":Ljava/lang/Exception;
    sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "Error while decrypting: "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v0}, Ljava/lang/Exception;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/io/PrintStream;->println(Ljava/lang/String;)V

    .line 49
    .end local v0    # "e":Ljava/lang/Exception;
    const/4 v0, 0x0

    return-object v0
.end method

.method public static setKey(Ljava/lang/String;)V
    .locals 4
    .param p0, "myKey"    # Ljava/lang/String;

    .line 20
    const/4 v0, 0x0

    .line 22
    .local v0, "sha":Ljava/security/MessageDigest;
    :try_start_0
    const-string v1, "UTF-8"

    invoke-virtual {p0, v1}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B

    move-result-object v1

    sput-object v1, Lcom/example/helloworld/DecryptString;->key:[B

    .line 23
    const-string v1, "SHA-1"

    invoke-static {v1}, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;

    move-result-object v1

    move-object v0, v1

    .line 24
    sget-object v1, Lcom/example/helloworld/DecryptString;->key:[B

    invoke-virtual {v0, v1}, Ljava/security/MessageDigest;->digest([B)[B

    move-result-object v1

    sput-object v1, Lcom/example/helloworld/DecryptString;->key:[B

    .line 25
    const/16 v2, 0x10

    invoke-static {v1, v2}, Ljava/util/Arrays;->copyOf([BI)[B

    move-result-object v1

    sput-object v1, Lcom/example/helloworld/DecryptString;->key:[B

    .line 26
    new-instance v1, Ljavax/crypto/spec/SecretKeySpec;

    sget-object v2, Lcom/example/helloworld/DecryptString;->key:[B

    const-string v3, "AES"

    invoke-direct {v1, v2, v3}, Ljavax/crypto/spec/SecretKeySpec;-><init>([BLjava/lang/String;)V

    sput-object v1, Lcom/example/helloworld/DecryptString;->secretKey:Ljavax/crypto/spec/SecretKeySpec;
    :try_end_0
    .catch Ljava/security/NoSuchAlgorithmException; {:try_start_0 .. :try_end_0} :catch_1
    .catch Ljava/io/UnsupportedEncodingException; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    .line 31
    :catch_0
    move-exception v1

    .line 32
    .local v1, "e":Ljava/io/UnsupportedEncodingException;
    invoke-virtual {v1}, Ljava/io/UnsupportedEncodingException;->printStackTrace()V

    goto :goto_1

    .line 28
    .end local v1    # "e":Ljava/io/UnsupportedEncodingException;
    :catch_1
    move-exception v1

    .line 29
    .local v1, "e":Ljava/security/NoSuchAlgorithmException;
    invoke-virtual {v1}, Ljava/security/NoSuchAlgorithmException;->printStackTrace()V

    .line 33
    .end local v1    # "e":Ljava/security/NoSuchAlgorithmException;
    :goto_0
    nop

    .line 34
    :goto_1
    return-void
.end method
