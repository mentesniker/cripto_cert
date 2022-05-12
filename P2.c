#include <stdio.h>
#include <stdlib.h>
typedef unsigned char Byte;

int contains(char *buffer, long filelen, Byte* numbers){
    int i = 0;
    while(i < filelen){
        
        if( i + 17 < filelen &&
            numbers[0] == buffer[i] &&
            numbers[1] == buffer[i+1] &&
            numbers[2] == buffer[i+2] &&
            numbers[3] == buffer[i+3] &&
            numbers[4] == buffer[i+4] &&
            numbers[5] == buffer[i+5] &&
            numbers[6] == buffer[i+6] &&
            numbers[7] == buffer[i+7] &&
            numbers[8] == buffer[i+8] &&
            numbers[9] == buffer[i+9] &&
            numbers[10] == buffer[i+10] 
        ){
            return 1;
        }
        i += 1;
    }
    return 0;
}

int main(int argc, char *argv[]) {

    printf("Leyendo el archivo %s...\n", argv[1]);

    FILE *fileptr;
    char *buffer;
    long filelen;

    fileptr = fopen(argv[1], "rb");               // Open the file in binary mode
    fseek(fileptr, 0, SEEK_END);                        // Jump to the end of the file 57FD6325.VBN malware.bin
    filelen = ftell(fileptr);                          // Get the current byte offset in the file
    rewind(fileptr);                                  // Jump back to the beginning of the file
    buffer = (char *)malloc(filelen * sizeof(char)); // Enough memory for the file
    fread(buffer, filelen, 1, fileptr);             // Read in the entire file
    fclose(fileptr);                               // Close the file

    Byte * tests = (Byte *)malloc(17 * sizeof(Byte));

    tests[0] = 0x54;
    tests[1] = 0x68;
    tests[2] = 0x69;
    tests[3] = 0x73;
    tests[4] = 0x20;
    tests[5] = 0x70;
    tests[6] = 0x72;
    tests[7] = 0x6f;
    tests[8] = 0x67;
    tests[9] = 0x72;
    tests[10] = 0x61;

    int i;                             
    char * buffer_out;
    FILE * fileptrout = fopen(argv[2], "wb"); 
    for(int key = 0; key < 255; key++){
        i = 0;
        buffer_out = (char *)malloc(filelen * sizeof(char));
        while(i < filelen){
            buffer_out[i] = buffer[i] ^ key;
            i += 1;
        }
        if(contains(buffer_out, filelen, tests)){
            fwrite(buffer_out, sizeof(buffer_out), filelen, fileptrout);
            printf("La llave fue %d\n", key);
            break;
        }
    }

    printf("Se escribio el archivo %s con la informacion descifrada.\n", argv[2]);
}