
#define ARRAY_SIZE(array) ((sizeof(array))/(sizeof(int)))


int sizeOfArray = 100;
int a[101];
  long counter = 0;
  float trueavg = 5;
  float truesd = 1;


void setup() {
  Serial.begin(115200);
  
}


void loop() {

  if (counter<sizeOfArray){
      a[counter] = analogRead(A6);
      Serial.print("COUNTER:");
      Serial.print(counter);
      
      Serial.print(", VALUE:");
      Serial.print(a[counter]);

      counter++;
    }

  else{
    a[sizeOfArray] = analogRead(A6);
    Serial.print("LASTVALUE:");
      Serial.print(a[sizeOfArray]);
      for (int i = 0; i < sizeOfArray; ++i){ 
          a[i] = a[i+1];
        }
//    printArray(a);
  }

  Serial.print(", Average:");
  trueavg = getMean(a, sizeOfArray);  
  Serial.print(trueavg);  
   

Serial.print(", SD:");
  truesd = getStdDev(a, sizeOfArray);  
  Serial.print(truesd);  
  Serial.print("\n"); 

  
  delay(100);
}

void printArray(int b[]){
  Serial.print("[");
  for(int i = 0; i < sizeOfArray; i++)
    {
      Serial.print(b[i]);
      Serial.print(",");
    }
  Serial.print("]");
}

float getMean(int * val, int arrayCount) {
  long total = 0;
  for (int i = 0; i < arrayCount; i++) {
    total = total + val[i];
  }
  float avg = total/(float)arrayCount;
  return avg;
}

float getStdDev(int * val, int arrayCount) {
  float avg = getMean(val, arrayCount);
  long total = 0;
  for (int i = 0; i < arrayCount; i++) {
    total = total + (val[i] - avg) * (val[i] - avg);
  }

  float variance = total/(float)arrayCount;
  float stdDev = sqrt(variance);
  return stdDev;
}
