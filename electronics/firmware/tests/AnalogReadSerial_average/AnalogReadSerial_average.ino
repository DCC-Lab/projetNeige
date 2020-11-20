
#define ARRAY_SIZE(array) ((sizeof(array))/(sizeof(int)))
#define PIN_A3   (17)
#define PIN_A4   (18)
#define PIN_A5   (19)
#define PIN_A6   (20)

int const sizeDataPD = 101;
int dataPD1[sizeDataPD];
int dataPD2[sizeDataPD];
int dataPD3[sizeDataPD];
int dataPD4[sizeDataPD];
unsigned int initializationCounter = 0;
unsigned int generalCounter = 0;
float trueavg = 0;
float truesd = 0;

static const uint8_t pd1Pin = PIN_A6;
static const uint8_t pd2Pin = PIN_A5;
static const uint8_t pd3Pin = PIN_A4;
static const uint8_t pd4Pin = PIN_A3;

void setup() {
  Serial.begin(115200);
}


void loop() {

  if (initializationCounter < sizeDataPD) {
    acquire_all(initializationCounter);
    initializationCounter++;
  }

  else {
    acquire_all(sizeDataPD);
    for (int i = 0; i < sizeDataPD; ++i) {
      dataPD1[i] = dataPD1[i + 1];
      dataPD2[i] = dataPD2[i + 1];
      dataPD3[i] = dataPD3[i + 1];
      dataPD4[i] = dataPD4[i + 1];
    }

  }

  if (generalCounter == 100) {
    stats_and_print(dataPD1, sizeDataPD, 1);
    stats_and_print(dataPD2, sizeDataPD, 2);
    stats_and_print(dataPD3, sizeDataPD, 3);
    stats_and_print(dataPD4, sizeDataPD, 4);
    generalCounter = 0;
  }
  
  generalCounter++;
}

void stats_and_print(int data[], int sizeData, int index){
    trueavg = getMean(data, sizeDataPD);
    truesd = getStdDev(data, sizeDataPD);
    Serial.print("AVG-");
    Serial.print(index);
    Serial.print("=");
    Serial.print(trueavg);
    Serial.print("\t");
    
    Serial.print("SD-");
    Serial.print(index);
    Serial.print("=");
    Serial.print(truesd);
    Serial.print("\t");
    
    Serial.print("\n");
}

void acquire_all(int index) {
  dataPD1[index] = analogRead(pd1Pin);
  dataPD2[index] = analogRead(pd2Pin);
  dataPD3[index] = analogRead(pd3Pin);
  dataPD4[index] = analogRead(pd4Pin);
}

float getMean(int * val, int arrayCount) {
  long total = 0;
  for (int i = 0; i < arrayCount; i++) {
    total = total + val[i];
  }
  float avg = total / (float)arrayCount;
  return avg;
}

float getStdDev(int * val, int arrayCount) {
  float avg = getMean(val, arrayCount);
  long total = 0;
  for (int i = 0; i < arrayCount; i++) {
    total = total + (val[i] - avg) * (val[i] - avg);
  }

  float variance = total / (float)arrayCount;
  float stdDev = sqrt(variance);
  return stdDev;
}
