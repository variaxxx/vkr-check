export const iconsConfig = {
  assetsPath: "icons",
  icons: [
    "logo",
    "upload",
    "history",
    "user",
    "log-out",
    "document",
    "x",
    "file-x",
    "alert-circle",
    "check-circle",
    "clock",
  ] as const,
};

export type IconName = typeof iconsConfig.icons[number];
