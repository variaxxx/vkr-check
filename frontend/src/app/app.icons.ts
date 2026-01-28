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
    "alert-triangle",
    "info",
    "search",
    "filter",
    "download",
    "refresh",
    "chevron-left",
    "chevron-right",
  ] as const,
};

export type IconName = typeof iconsConfig.icons[number];
