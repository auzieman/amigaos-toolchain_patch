/* SPDX-License-Identifier: MIT. Diagnostic static USB input config, no hotplug. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
int main(void) {
 if(geteuid()!=0){fputs("Run from the root rescue console; E itself stays a normal user.\n",stderr);return 1;}
 FILE *in=fopen("/proc/bus/input/devices","r");if(!in)return 2;
 char line[1024],keyboard[32]="",mouse[32]="";
 while(fgets(line,sizeof line,in)) {
  if(strncmp(line,"H: Handlers=",12))continue;char *event=strstr(line,"event");if(!event)continue;
  char name[32];size_t n=strspn(event+5,"0123456789");if(!n||n>10)continue;snprintf(name,sizeof name,"event%.*s",(int)n,event+5);
  if(strstr(line,"kbd")&&!keyboard[0])strcpy(keyboard,name);
  if(strstr(line,"mouse")&&!mouse[0])strcpy(mouse,name);
 }
 fclose(in);if(!keyboard[0]){fputs("No evdev keyboard detected; leave rescue console/SSH available.\n",stderr);return 3;}
 FILE *f=fopen("/tmp/tabor-xorg.conf","w");if(!f)return 4;
 fputs("Section \"ServerFlags\"\n Option \"AutoAddDevices\" \"false\"\nEndSection\nSection \"Device\"\n Identifier \"RadeonKMS\"\n Driver \"modesetting\"\n Option \"AccelMethod\" \"none\"\n Option \"PageFlip\" \"false\"\n Option \"ShadowFB\" \"true\"\nEndSection\nSection \"Screen\"\n Identifier \"Screen0\"\n Device \"RadeonKMS\"\n DefaultDepth 24\nEndSection\n",f);
 fprintf(f,"Section \"InputDevice\"\n Identifier \"Keyboard0\"\n Driver \"evdev\"\n Option \"Device\" \"/dev/input/%s\"\n Option \"XkbLayout\" \"us\"\nEndSection\n",keyboard);
 if(mouse[0])fprintf(f,"Section \"InputDevice\"\n Identifier \"Mouse0\"\n Driver \"evdev\"\n Option \"Device\" \"/dev/input/%s\"\nEndSection\n",mouse);
 fprintf(f,"Section \"ServerLayout\"\n Identifier \"TaborDiagnostic\"\n Screen \"Screen0\"\n InputDevice \"Keyboard0\" \"CoreKeyboard\"\n%sEndSection\n",mouse[0]?" InputDevice \"Mouse0\" \"CorePointer\"\n":"");
 if(fclose(f))return 5;printf("Configured keyboard=%s mouse=%s; static KMS/evdev diagnostic only.\n",keyboard,mouse[0]?mouse:"none");return 0;
}
