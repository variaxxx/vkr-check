export const iconsConfig = {
  assetsPath: "icons",
  icons: [
    "logo",
    "upload",
    "history",
    "user",
  ] as const,
};

export type IconName = typeof iconsConfig.icons[number];
