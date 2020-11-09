
#define ARRAY_SIZE(array) ((sizeof(array))/(sizeof(array[0])))


int lastIndex = 100;
int a[101];
long counter = 0;



void setup() {
  Serial.begin(115200);
}


void loop() {

  if (counter<lastIndex){
      a[counter] = analogRead(A0);
      Serial.print("VALUE:");
      Serial.print(a[counter]);

      counter++;
    }

  else{
    a[lastIndex] = analogRead(A0);
    Serial.print("VALUE:");
      Serial.print(a[lastIndex]);
      for (int i = 0; i < lastIndex; ++i){ 
          a[i] = a[i+1];
        }
  }

  Serial.print(", Average:");
  Serial.print(average_array(a));  
  Serial.print("\n");  
  delay(10);
}


int average_array(int b[]){
  int s = 0;
  int avg = 0;
  for (int i=0;i<ARRAY_SIZE(b);i++){
      Serial.print(s);
      s += b[i];
  }
  avg = s/(ARRAY_SIZE(b));
  return avg;
}
