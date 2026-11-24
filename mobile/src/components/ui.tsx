/**
 * Small building blocks used by every screen, so they all look the same.
 * They follow the "Components" page of the Figma design (design/components.svg).
 */
import Ionicons from '@expo/vector-icons/Ionicons';
import { type ComponentProps, type ReactNode, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  type StyleProp,
  StyleSheet,
  Text,
  TextInput,
  type TextInputProps,
  View,
  type ViewStyle,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { maskDate } from '@/lib/dates';

import { colors, fonts, radius, shadows, space, type } from './theme';

export type IconName = ComponentProps<typeof Ionicons>['name'];

export function Icon({
  name,
  size = 20,
  color = colors.text,
}: {
  name: IconName;
  size?: number;
  color?: ComponentProps<typeof Ionicons>['color'];
}) {
  return <Ionicons name={name} size={size} color={color} />;
}

// --- Layout ----------------------------------------------------------------

export function Screen({
  children,
  scroll = true,
  topInset = true,
}: {
  children: ReactNode;
  scroll?: boolean;
  topInset?: boolean; // false on screens that already have a header
}) {
  return (
    <SafeAreaView style={styles.screen} edges={topInset ? ['top', 'left', 'right'] : ['left', 'right']}>
      {scroll ? (
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
          {children}
        </ScrollView>
      ) : (
        <View style={[styles.content, { flex: 1 }]}>{children}</View>
      )}
    </SafeAreaView>
  );
}

// --- Text ------------------------------------------------------------------

/** Big serif page title (Playfair Display). */
export function Title({ children }: { children: ReactNode }) {
  return <Text style={[type.title, { color: colors.text }]}>{children}</Text>;
}

export function Heading({ children }: { children: ReactNode }) {
  return <Text style={[type.heading, { color: colors.text }]}>{children}</Text>;
}

export function Subtitle({ children }: { children: ReactNode }) {
  return <Text style={[type.body, { color: colors.muted }]}>{children}</Text>;
}

/** Small caps label above a form field. */
export function Label({ children }: { children: ReactNode }) {
  return <Text style={[type.captionStrong, { color: colors.muted }]}>{children}</Text>;
}

/** Section header: "НАШЕ ЛЮБИМОЕ", optionally with an action on the right ("Все"). */
export function SectionTitle({
  children,
  action,
  onAction,
}: {
  children: ReactNode;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <View style={styles.sectionTitle}>
      <Text style={[type.label, { color: colors.muted }]}>{children}</Text>
      {action && onAction ? (
        <Pressable accessibilityRole="button" onPress={onAction} hitSlop={10}>
          <Text style={[type.captionStrong, { color: colors.text }]}>{action}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

export function ErrorText({ children }: { children: ReactNode }) {
  if (!children) return null;
  return (
    <View style={styles.warning}>
      <Icon name="alert-circle-outline" size={16} color={colors.danger} />
      <Text style={[type.caption, { color: colors.danger, flex: 1 }]}>{children}</Text>
    </View>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <Text style={[type.body, { color: colors.muted, paddingVertical: space.md }]}>{children}</Text>;
}

// --- Containers ------------------------------------------------------------

/** default — white with a border; surface — grey block; dark — the black accent card. */
export function Card({
  children,
  style,
  variant = 'default',
}: {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  variant?: 'default' | 'surface' | 'dark';
}) {
  return <View style={[styles.card, styles[`card_${variant}`], style]}>{children}</View>;
}

/** A round avatar with the first letter of a name. */
export function Avatar({
  name,
  size = 40,
  dark = false,
  style,
}: {
  name: string;
  size?: number;
  dark?: boolean;
  style?: StyleProp<ViewStyle>;
}) {
  return (
    <View
      style={[
        {
          width: size,
          height: size,
          borderRadius: size / 2,
          backgroundColor: dark ? colors.black : colors.surface2,
          alignItems: 'center',
          justifyContent: 'center',
        },
        style,
      ]}>
      <Text style={{ fontFamily: fonts.serif, fontSize: size * 0.45, color: dark ? '#fff' : colors.text }}>
        {name.slice(0, 1).toUpperCase()}
      </Text>
    </View>
  );
}

// --- Buttons ---------------------------------------------------------------

type ButtonKind = 'primary' | 'secondary' | 'text' | 'danger' | 'ghost'; // ghost = old name for text

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'normal',
  icon,
  loading = false,
  disabled = false,
  style,
}: {
  title: string;
  onPress: () => void;
  variant?: ButtonKind;
  size?: 'normal' | 'small';
  icon?: IconName;
  loading?: boolean;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
}) {
  const kind = variant === 'ghost' ? 'text' : variant;
  const isDisabled = disabled || loading;
  const textColor = kind === 'primary' || kind === 'danger' ? '#fff' : colors.text;
  const small = size === 'small';

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      onPress={onPress}
      disabled={isDisabled}
      style={({ pressed }) => [
        styles.button,
        small && styles.buttonSmall,
        kind === 'primary' && { backgroundColor: pressed ? colors.blackPressed : colors.black },
        kind === 'danger' && { backgroundColor: pressed ? '#B42F2F' : colors.danger },
        kind === 'secondary' && [styles.buttonSecondary, pressed && { backgroundColor: colors.surface }],
        kind === 'text' && pressed && { backgroundColor: colors.surface },
        disabled && kind === 'primary' && { backgroundColor: colors.surface2 },
        disabled && kind === 'secondary' && { borderColor: colors.border },
        disabled && kind === 'danger' && { backgroundColor: '#F2C4C4' },
        style,
      ]}>
      {loading ? (
        <ActivityIndicator color={textColor} />
      ) : (
        <View style={styles.buttonInner}>
          {icon ? <Icon name={icon} color={disabled ? colors.subtle : textColor} size={small ? 16 : 18} /> : null}
          <Text
            style={[
              type.button,
              small && { fontSize: 14 },
              { color: textColor },
              disabled && kind !== 'danger' && { color: colors.subtle },
            ]}>
            {title}
          </Text>
        </View>
      )}
    </Pressable>
  );
}

/** The round black "+" in the bottom-right corner. */
export function Fab({ onPress, label }: { onPress: () => void; label: string }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      style={({ pressed }) => [styles.fab, pressed && { backgroundColor: colors.blackPressed }]}>
      <Icon name="add" size={28} color="#fff" />
    </Pressable>
  );
}

/** A round grey icon button, e.g. the bell in a header (with an unread counter). */
export function IconButton({
  name,
  onPress,
  label,
  badge = 0,
}: {
  name: IconName;
  onPress: () => void;
  label: string;
  badge?: number;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      hitSlop={6}
      style={({ pressed }) => [styles.iconButton, pressed && { backgroundColor: colors.surface2 }]}>
      <Icon name={name} size={20} />
      {badge > 0 ? (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{badge > 99 ? '99+' : badge}</Text>
        </View>
      ) : null}
    </Pressable>
  );
}

// --- Choices ---------------------------------------------------------------

/**
 * A pill for filters and choices. Single choice: black when selected.
 * `multi`: a check mark appears when selected. `icon`: shown on the left.
 */
export function Chip({
  label,
  selected,
  onPress,
  icon,
  multi = false,
  danger = false,
}: {
  label: string;
  selected: boolean;
  onPress: () => void;
  icon?: IconName;
  multi?: boolean;
  danger?: boolean;
}) {
  const iconColor = selected ? '#fff' : danger ? colors.danger : colors.text;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ selected }}
      onPress={onPress}
      style={[styles.chip, selected && styles.chipSelected]}>
      {multi && selected ? <Icon name="checkmark" size={14} color="#fff" /> : null}
      {icon ? <Icon name={icon} size={14} color={icon.startsWith('heart') ? colors.heart : iconColor} /> : null}
      <Text style={[type.captionStrong, { fontSize: 14, color: selected ? '#fff' : colors.text }]}>{label}</Text>
    </Pressable>
  );
}

export function ChipRow({ children }: { children: ReactNode }) {
  return <View style={styles.chipRow}>{children}</View>;
}

/** A small grey label on a card: "Поесть", "₽₽", "Вечер". */
export function Tag({ label, icon }: { label: string; icon?: IconName }) {
  return (
    <View style={styles.tag}>
      {icon ? <Icon name={icon} size={12} color={colors.muted} /> : null}
      <Text style={[type.tag, { color: colors.muted }]}>{label}</Text>
    </View>
  );
}

/** Two or three options side by side. */
export function Segmented<K extends string>({
  options,
  value,
  onChange,
}: {
  options: Record<K, string>;
  value: K;
  onChange: (key: K) => void;
}) {
  return (
    <View style={styles.segmented}>
      {(Object.keys(options) as K[]).map((key) => (
        <Pressable
          key={key}
          accessibilityRole="button"
          accessibilityState={{ selected: value === key }}
          onPress={() => onChange(key)}
          style={[styles.segment, value === key && styles.segmentSelected]}>
          <Text style={[type.captionStrong, { fontSize: 14, color: value === key ? colors.text : colors.muted }]}>
            {options[key]}
          </Text>
        </Pressable>
      ))}
    </View>
  );
}

// --- Inputs ----------------------------------------------------------------

/** A text field: grey at rest, black border while typing, red border with an error. */
export function Input(props: TextInputProps & { label?: string; error?: string }) {
  const { label, error, style, onFocus, onBlur, ...rest } = props;
  const [focused, setFocused] = useState(false);
  return (
    <View style={{ gap: 6 }}>
      {label ? <Label>{label}</Label> : null}
      <TextInput
        placeholderTextColor={colors.subtle}
        onFocus={(e) => {
          setFocused(true);
          onFocus?.(e);
        }}
        onBlur={(e) => {
          setFocused(false);
          onBlur?.(e);
        }}
        style={[
          styles.input,
          focused && styles.inputFocused,
          !!error && styles.inputError,
          style,
        ]}
        {...rest}
      />
      {error ? <ErrorText>{error}</ErrorText> : null}
    </View>
  );
}

/** A date typed as ДД.ММ.ГГГГ; dots are added automatically. */
export function DateInput({
  label,
  value,
  onChangeText,
}: {
  label?: string;
  value: string;
  onChangeText: (text: string) => void;
}) {
  return (
    <Input
      label={label}
      value={value}
      onChangeText={(text) => onChangeText(maskDate(text))}
      placeholder="ДД.ММ.ГГГГ"
      keyboardType="number-pad"
      maxLength={10}
    />
  );
}

// --- Lists -----------------------------------------------------------------

/** A list row: icon in a grey circle, title, subtitle, value and a chevron. */
export function Row({
  icon,
  title,
  subtitle,
  value,
  onPress,
  danger = false,
}: {
  icon?: IconName;
  title: string;
  subtitle?: string;
  value?: string;
  onPress?: () => void;
  danger?: boolean;
}) {
  const color = danger ? colors.danger : colors.text;
  return (
    <Pressable
      accessibilityRole={onPress ? 'button' : undefined}
      onPress={onPress}
      disabled={!onPress}
      style={({ pressed }) => [styles.row, pressed && { backgroundColor: colors.surface }]}>
      {icon ? (
        <View style={[styles.rowIcon, danger && { backgroundColor: colors.dangerSoft }]}>
          <Icon name={icon} color={color} size={18} />
        </View>
      ) : null}
      <View style={{ flex: 1, gap: 2 }}>
        <Text style={[type.bodyStrong, { color }]}>{title}</Text>
        {subtitle ? <Text style={[type.caption, { color: colors.muted }]}>{subtitle}</Text> : null}
      </View>
      {value ? <Text style={[type.caption, { color: colors.muted }]}>{value}</Text> : null}
      {onPress && !danger ? <Icon name="chevron-forward-outline" color={colors.subtle} size={18} /> : null}
    </Pressable>
  );
}

export function Loading() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: space.xl }}>
      <ActivityIndicator color={colors.black} size="large" />
    </View>
  );
}

/** A grey placeholder block shown while data loads. */
export function Skeleton({ height, style }: { height: number; style?: StyleProp<ViewStyle> }) {
  return <View style={[{ height, borderRadius: radius.xl, backgroundColor: colors.skeleton }, style]} />;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  content: { padding: space.md, gap: space.md, paddingBottom: 120 },
  sectionTitle: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: space.sm,
  },
  warning: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  card: { borderRadius: radius.xl, padding: space.md, gap: space.sm },
  card_default: { backgroundColor: colors.background, borderWidth: 1, borderColor: colors.border },
  card_surface: { backgroundColor: colors.surface },
  card_dark: { backgroundColor: colors.black, borderRadius: radius.xxl },
  button: {
    minHeight: 52,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: space.md,
  },
  buttonSmall: { minHeight: 40, borderRadius: radius.sm, paddingHorizontal: 14, alignSelf: 'flex-start' },
  buttonInner: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  buttonSecondary: { borderWidth: 1.5, borderColor: colors.black, backgroundColor: colors.background },
  fab: {
    position: 'absolute',
    right: space.md,
    bottom: space.md,
    width: 56,
    height: 56,
    borderRadius: radius.pill,
    backgroundColor: colors.black,
    alignItems: 'center',
    justifyContent: 'center',
    ...shadows.md,
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  badge: {
    position: 'absolute',
    top: -3,
    right: -3,
    minWidth: 18,
    height: 18,
    paddingHorizontal: 4,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: colors.background,
    backgroundColor: colors.heart,
    alignItems: 'center',
    justifyContent: 'center',
  },
  badgeText: { color: '#fff', fontSize: 10, fontFamily: fonts.bold },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    minHeight: 36,
    paddingHorizontal: 14,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.background,
  },
  chipSelected: { backgroundColor: colors.black, borderColor: colors.black },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
  tag: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    height: 26,
    paddingHorizontal: 10,
    borderRadius: radius.xs,
    backgroundColor: colors.surface,
  },
  segmented: { flexDirection: 'row', backgroundColor: colors.surface, borderRadius: radius.md, padding: 4 },
  segment: { flex: 1, minHeight: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
  segmentSelected: { backgroundColor: colors.background, ...shadows.sm },
  input: {
    minHeight: 52,
    borderRadius: radius.md,
    borderWidth: 1.5,
    borderColor: colors.surface,
    backgroundColor: colors.surface,
    paddingHorizontal: space.md,
    fontFamily: fonts.medium,
    fontSize: 16,
    color: colors.text,
  },
  inputFocused: { borderColor: colors.black, backgroundColor: colors.background },
  inputError: { borderColor: colors.danger, backgroundColor: colors.background },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 12,
    paddingHorizontal: space.md,
  },
  rowIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
