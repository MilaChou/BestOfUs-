/** Design tokens from the Figma file (design/styles.svg). Names match the design. */
export const colors = {
  background: '#FFFFFF', // screen background
  surface: '#F5F4F2', // grey blocks, input fields
  surface2: '#ECEAE6', // dividers on grey blocks
  border: '#E6E3DF', // card borders
  text: '#111111',
  muted: '#6E6A66', // secondary text (text-muted)
  subtle: '#A6A29D', // placeholders, inactive (text-subtle)
  black: '#111111', // buttons, dark cards
  blackPressed: '#3A3836',
  heart: '#E85D75', // hearts, "both", counters (accent-heart)
  heartSoft: '#FCE9ED', // background under a heart
  danger: '#D63B3B', // errors, overdue, delete
  dangerSoft: '#FBEAEA',
  skeleton: '#EFEDEA', // loading placeholders
};

export const space = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32, block: 28 };
// xs 8 tags · sm 12 small buttons · md 14 inputs · lg 16 buttons/photos · xl 20 cards · xxl 24 hero card
export const radius = { xs: 8, sm: 12, md: 14, lg: 16, xl: 20, xxl: 24, pill: 999 };

/**
 * Font files loaded in app/_layout.tsx. With custom fonts, Android ignores
 * fontWeight, so every weight is its own family name.
 */
export const fonts = {
  regular: 'Manrope_400Regular',
  medium: 'Manrope_500Medium',
  semibold: 'Manrope_600SemiBold',
  bold: 'Manrope_700Bold',
  extrabold: 'Manrope_800ExtraBold',
  serif: 'PlayfairDisplay_600SemiBold',
};

/** Text styles from the design (size / line height · letter spacing). */
export const type = {
  display: { fontFamily: fonts.serif, fontSize: 104, lineHeight: 108, letterSpacing: -2 },
  title: { fontFamily: fonts.serif, fontSize: 32, lineHeight: 40, letterSpacing: -0.3 },
  titleS: { fontFamily: fonts.serif, fontSize: 24, lineHeight: 30, letterSpacing: -0.2 },
  heading: { fontFamily: fonts.bold, fontSize: 20, lineHeight: 28, letterSpacing: -0.2 },
  subheading: { fontFamily: fonts.bold, fontSize: 17, lineHeight: 24, letterSpacing: -0.1 },
  body: { fontFamily: fonts.medium, fontSize: 15, lineHeight: 22 },
  bodyStrong: { fontFamily: fonts.semibold, fontSize: 15, lineHeight: 22 },
  caption: { fontFamily: fonts.medium, fontSize: 13, lineHeight: 18 },
  captionStrong: { fontFamily: fonts.semibold, fontSize: 13, lineHeight: 18 },
  label: { fontFamily: fonts.bold, fontSize: 12, lineHeight: 16, letterSpacing: 1.2, textTransform: 'uppercase' as const },
  button: { fontFamily: fonts.bold, fontSize: 15, lineHeight: 20 },
  tab: { fontFamily: fonts.semibold, fontSize: 11, lineHeight: 16 }, // 16, not 14: Manrope's descenders (д, у) need room
  tag: { fontFamily: fonts.semibold, fontSize: 12, lineHeight: 16 },
  code: { fontFamily: fonts.extrabold, fontSize: 28, lineHeight: 34, letterSpacing: 4 },
  number: { fontFamily: fonts.extrabold, fontSize: 20, lineHeight: 24, letterSpacing: -0.2 },
};

/** Only things that float above the content get a shadow. */
export const shadows = {
  sm: { shadowColor: '#000', shadowOpacity: 0.08, shadowRadius: 3, shadowOffset: { width: 0, height: 1 }, elevation: 1 },
  md: { shadowColor: '#000', shadowOpacity: 0.12, shadowRadius: 18, shadowOffset: { width: 0, height: 6 }, elevation: 6 },
  up: { shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 16, shadowOffset: { width: 0, height: -2 }, elevation: 8 },
};
