long one_dur = 0;
long zero_dur = 0;
long guard = 0;

// wait specified duration
void wait(long dur) {
    if (dur < 16000) {
        delayMicroseconds(dur);
    } else {
        delay(dur / 1000);
    }
}

// send binary one
void one() {
    digitalWrite(53, HIGH);
    wait(one_dur);
    //delayMicroseconds(15);
    digitalWrite(53, LOW);
    wait(guard);
    //delayMicroseconds(15);
}

// send binary zero
void zero() {
    digitalWrite(53, HIGH);
    wait(zero_dur);
    //delayMicroseconds(50);
    digitalWrite(53, LOW);
    wait(guard);
    //delayMicroseconds(15);
}

// send character
void send(char c) {
    for (int n = 7; n > -1; n--) {
        if (c & (1 << n)) {
            one();
        } else {
            zero();
        }
    }
}

// send data loop, after init
void sendData() {
    long len;
    char *data;
    while (1) {
        if (Serial.available() > 0) {
            len = Serial.parseInt();
            Serial.read();                  // get \n

            data = (char *) malloc(len);
            if (data == NULL) {
                Serial.write(0x01);
                continue;
            } else {
                Serial.write(0x00);
            }
            memset(data, '\0', len);
            Serial.readBytes(data, len);
            for (int i = 0; i < len; i++) {
                send(data[i]);
            }
            free(data);
            Serial.write(0x00);
        }
    }
}

// configure pins
void setup() {
    pinMode(53, OUTPUT);
    Serial.begin(115200);
    Serial.write(0x00);
}

// loop through transmissions
void loop() {
    if (Serial.available() > 0) {
        one_dur = Serial.parseInt();
        Serial.read();
        zero_dur = Serial.parseInt();
        Serial.read();
        guard = Serial.parseInt();
        Serial.read();
        Serial.write(0x00);
        sendData();
    }
}
