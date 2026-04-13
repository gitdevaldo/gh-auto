{pkgs}: {
  deps = [
    pkgs.alsa-lib
    pkgs.xorg.libXrender
    pkgs.xorg.libXt
    pkgs.dbus-glib
    pkgs.glib
    pkgs.gtk3
  ];
}
