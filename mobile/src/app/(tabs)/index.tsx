import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { useAuth, usePartner } from '@/auth/auth-context';
import { InviteBanner } from '@/components/invite-banner';
import { TabHeader } from '@/components/tab-header';
import { colors, radius, space, type } from '@/components/theme';
import { Avatar, Button, Card, Icon, type IconName, Screen, SectionTitle } from '@/components/ui';
import { daysUntilYearly, formatDate, inDays, plural } from '@/lib/dates';
import { loadResult } from '@/lib/tests';
import type { Profile, ProfileField, TestResult } from '@/lib/types';

/** What we show side by side in "Наше любимое". */
const FAVORITES: { key: ProfileField; label: string }[] = [
  { key: 'favorite_food', label: 'Еда' },
  { key: 'favorite_drink', label: 'Напиток' },
  { key: 'favorite_flowers', label: 'Цветы' },
  { key: 'favorite_color', label: 'Цвет' },
];

/** A colour dot next to "Любимый цвет" when we recognise the colour name. */
const COLOR_WORDS: [string, string][] = [
  ['тёмно-син', '#1F2A4A'],
  ['темно-син', '#1F2A4A'],
  ['пудров', '#E8C5BE'],
  ['голуб', '#8EC5E8'],
  ['син', '#2F5DA8'],
  ['бордо', '#7A1F2B'],
  ['красн', '#D63B3B'],
  ['розов', '#E85D75'],
  ['фиолет', '#7B5EA7'],
  ['лаванд', '#B9A7D8'],
  ['зелён', '#3E8E5A'],
  ['зелен', '#3E8E5A'],
  ['мятн', '#9ED9C3'],
  ['жёлт', '#F2C94C'],
  ['желт', '#F2C94C'],
  ['оранж', '#F2994A'],
  ['бежев', '#D9C3A5'],
  ['серый', '#9A9590'],
  ['чёрн', '#111111'],
  ['черн', '#111111'],
  ['бел', '#FFFFFF'],
];

function colorOf(name: string | null): string | null {
  if (!name) return null;
  const lower = name.toLowerCase();
  return COLOR_WORDS.find(([word]) => lower.includes(word))?.[1] ?? null;
}

type Upcoming = { icon: IconName; title: string; subtitle: string; when: number; love: boolean };

function upcoming(partner: Profile | null, together: string | null): Upcoming[] {
  const items: Upcoming[] = [];
  if (partner?.birth_date) {
    items.push({
      icon: 'gift-outline',
      title: partner.name,
      subtitle: `день рождения · ${formatDate(partner.birth_date, false)}`,
      when: daysUntilYearly(partner.birth_date),
      love: false,
    });
  }
  if (together) {
    const when = daysUntilYearly(together);
    // The year in which that next anniversary falls, minus the year we started.
    const nextDate = new Date(Date.now() + when * 86_400_000);
    const years = nextDate.getFullYear() - Number(together.slice(0, 4));
    if (years > 0) {
      items.push({
        icon: 'heart-outline',
        title: `Годовщина — ${years} ${plural(years, 'год', 'года', 'лет')}`,
        subtitle: formatDate(`${nextDate.getFullYear()}-${together.slice(5, 10)}`),
        when,
        love: true,
      });
    }
  }
  return items.sort((a, b) => a.when - b.when);
}

export default function UsScreen() {
  const { user, couple, refresh } = useAuth();
  const partner = usePartner();
  const [myLove, setMyLove] = useState<TestResult | null>(null);
  const [partnerLove, setPartnerLove] = useState<TestResult | null>(null);

  useFocusEffect(
    useCallback(() => {
      refresh().catch(() => {});
      loadResult('love', 'me').then(setMyLove).catch(() => {});
      loadResult('love', 'partner').then(setPartnerLove).catch(() => {});
    }, [refresh]),
  );

  if (!user) return null;
  const me = user.profile;
  const p = partner?.profile ?? null;
  const dates = upcoming(p, couple?.together_since ?? null);

  return (
    <Screen>
      <TabHeader title="Мы" />
      <Hero me={me} partner={p} coupleName={couple?.name ?? null} days={couple?.days_together ?? null} since={couple?.together_since ?? null} />
      <InviteBanner />

      <Block title="Скоро">
        {dates.length ? (
          <Card variant="surface" style={{ gap: 4 }}>
            {dates.map((d) => (
              <View key={d.title} style={styles.soonRow}>
                <View style={styles.soonIcon}>
                  <Icon name={d.icon} size={18} color={d.love ? colors.heart : colors.text} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[type.bodyStrong, { color: colors.text }]}>{d.title}</Text>
                  <Text style={[type.caption, { color: colors.muted }]}>{d.subtitle}</Text>
                </View>
                <When days={d.when} />
              </View>
            ))}
          </Card>
        ) : (
          <Card variant="surface" style={styles.inlineEmpty}>
            <Icon name="calendar-outline" size={20} color={colors.muted} />
            <Text style={[type.caption, { color: colors.muted, flex: 1 }]}>
              Здесь появятся дни рождения и годовщины
            </Text>
          </Card>
        )}
      </Block>

      <Block title="Мы двое">
        <View style={styles.twoCols}>
          <PersonCard
            name={me.name}
            petName={me.pet_name}
            description="Мой профиль и вишлист"
            onPress={() => router.push('/me')}
          />
          {p ? (
            <PersonCard
              name={p.name}
              petName={p.pet_name}
              description="Профиль, размеры, любимое, вишлист"
              dark
              onPress={() => router.push('/partner')}
            />
          ) : (
            <View style={[styles.person, styles.personMissing]}>
              <View style={styles.missingIcon}>
                <Icon name="person-add-outline" size={20} color={colors.muted} />
              </View>
              <Text style={[type.subheading, { color: colors.text }]}>Партнёр</Text>
              <Text style={[type.caption, { color: colors.muted }]}>Ещё не присоединился — отправьте код</Text>
            </View>
          )}
        </View>
      </Block>

      <Block
        title="Наши языки любви"
        action={myLove || partnerLove ? 'Результаты' : undefined}
        onAction={() =>
          router.push({ pathname: '/test-result', params: { test: 'love', whose: myLove ? 'me' : 'partner' } })
        }>
        {myLove || partnerLove ? (
          <Card variant="surface" style={styles.loveCard}>
            <LoveColumn
              name={me.name}
              result={myLove}
              onPress={() =>
                myLove
                  ? router.push({ pathname: '/test-result', params: { test: 'love', whose: 'me' } })
                  : router.push({ pathname: '/test/[id]', params: { id: 'love' } })
              }
              emptyText="Пройти тест"
            />
            <View style={styles.vDivider} />
            <LoveColumn
              name={p?.name ?? 'Партнёр'}
              result={partnerLove}
              onPress={() => (partnerLove ? router.push('/partner') : undefined)}
              emptyText="Тест не пройден"
            />
          </Card>
        ) : (
          <Card variant="surface" style={{ gap: 12 }}>
            <View style={styles.inlineRow}>
              <Icon name="chatbubbles-outline" size={20} />
              <View style={{ flex: 1 }}>
                <Text style={[type.bodyStrong, { color: colors.text }]}>Как вы чувствуете любовь?</Text>
                <Text style={[type.caption, { color: colors.muted }]}>Тест на 5 минут — 30 вопросов</Text>
              </View>
            </View>
            <Button title="Пройти тест" variant="secondary" size="small" onPress={() => router.push({ pathname: '/test/[id]', params: { id: 'love' } })} />
          </Card>
        )}
      </Block>

      <Block title="Наше любимое">
        <Favorites me={me} partner={p} />
      </Block>
    </Screen>
  );
}

// --- Pieces of the screen ----------------------------------------------------

function Block({
  title,
  action,
  onAction,
  children,
}: {
  title: string;
  action?: string;
  onAction?: () => void;
  children: React.ReactNode;
}) {
  return (
    <View style={{ gap: 12, marginTop: 4 }}>
      <SectionTitle action={action} onAction={onAction}>
        {title}
      </SectionTitle>
      {children}
    </View>
  );
}

/** The big black card: how many days together, or a prompt to set the date. */
function Hero({
  me,
  partner,
  coupleName,
  days,
  since,
}: {
  me: Profile;
  partner: Profile | null;
  coupleName: string | null;
  days: number | null;
  since: string | null;
}) {
  const names = coupleName ?? (partner ? `${me.name} и ${partner.name}` : me.name);
  const edit = () => router.push('/couple-edit');
  const hasDate = days !== null && !!since;

  const card = (
      <Card variant="dark" style={styles.hero}>
        <View style={styles.heroTop}>
          <View style={{ flexDirection: 'row' }}>
            <Avatar name={me.name} size={28} style={styles.heroAvatar} />
            {partner ? (
              <Avatar name={partner.name} size={28} style={[styles.heroAvatar, { marginLeft: -8 }]} />
            ) : (
              <View style={[styles.heroAvatar, styles.heroAvatarEmpty]}>
                <Icon name="add" size={14} color="#fff" />
              </View>
            )}
          </View>
          <Text style={[type.label, styles.heroLabel]} numberOfLines={1}>
            {names}
          </Text>
          {days !== null ? <Icon name="create-outline" size={18} color="rgba(255,255,255,0.6)" /> : null}
        </View>

        {hasDate ? (
          <>
            <View style={styles.heroNumberRow}>
              <Text style={[type.display, { color: '#fff' }]} numberOfLines={1} adjustsFontSizeToFit>
                {days}
              </Text>
              <View style={{ marginTop: 18, marginLeft: 4 }}>
                <Icon name="heart" size={22} color={colors.heart} />
              </View>
            </View>
            <Text style={[type.body, { color: 'rgba(255,255,255,0.7)' }]}>
              <Text style={[type.bodyStrong, { color: '#fff' }]}>
                {plural(days, 'день', 'дня', 'дней')} вместе
              </Text>
              {'  ·  '}с {formatDate(since!)}
            </Text>
          </>
        ) : (
          <>
            <Text style={[type.title, { color: '#fff', fontSize: 30, lineHeight: 38, marginTop: space.sm }]}>
              Укажите, когда вы начали встречаться
            </Text>
            <Text style={[type.caption, { color: 'rgba(255,255,255,0.7)' }]}>
              Будем считать дни и напоминать о годовщинах
            </Text>
            <Pressable accessibilityRole="button" onPress={edit} style={styles.heroButton}>
              <Icon name="calendar-outline" size={16} />
              <Text style={[type.button, { fontSize: 14, color: colors.text }]}>Указать дату</Text>
            </Pressable>
          </>
        )}
      </Card>
  );

  // With a date the whole card opens editing; without one only the "Указать дату" button does
  // (a button inside another button isn't allowed).
  if (!hasDate) return card;
  return (
    <Pressable onPress={edit} accessibilityRole="button" accessibilityLabel="Изменить дату и название пары">
      {card}
    </Pressable>
  );
}

/** "через / 6 дней" on the right of an upcoming date. */
function When({ days }: { days: number }) {
  if (days <= 1) {
    return <Text style={[type.bodyStrong, { color: colors.heart }]}>{inDays(days)}</Text>;
  }
  return (
    <View style={{ alignItems: 'flex-end' }}>
      <Text style={[type.caption, { color: colors.muted }]}>через</Text>
      <Text style={[type.bodyStrong, { color: colors.text }]}>
        {days} {plural(days, 'день', 'дня', 'дней')}
      </Text>
    </View>
  );
}

function PersonCard({
  name,
  petName,
  description,
  dark = false,
  onPress,
}: {
  name: string;
  petName: string | null;
  description: string;
  dark?: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={({ pressed }) => [styles.person, pressed && { backgroundColor: colors.surface }]}>
      <View style={styles.personTop}>
        <Avatar name={name} size={44} dark={dark} />
        <Icon name="chevron-forward-outline" size={18} color={colors.subtle} />
      </View>
      <Text style={[type.subheading, { color: colors.text }]} numberOfLines={1}>
        {name}
      </Text>
      {petName ? (
        <View style={styles.petName}>
          <Icon name="heart" size={11} color={colors.heart} />
          <Text style={[type.caption, { color: colors.muted }]} numberOfLines={1}>
            {petName}
          </Text>
        </View>
      ) : null}
      <Text style={[type.caption, { color: colors.muted }]}>{description}</Text>
    </Pressable>
  );
}

function LoveColumn({
  name,
  result,
  onPress,
  emptyText,
}: {
  name: string;
  result: TestResult | null;
  onPress: () => void;
  emptyText: string;
}) {
  const allEqual = !!result && result.leading.length === result.scores.length;
  const leading = allEqual ? [] : (result?.scores.filter((s) => result.leading.includes(s.key)) ?? []);
  return (
    <Pressable onPress={onPress} style={{ flex: 1, gap: 6 }}>
      <Text style={[type.caption, { color: colors.muted }]}>{name}</Text>
      {leading.length ? (
        leading.map((s) => (
          <Text key={s.key} style={[type.bodyStrong, { color: colors.text }]}>
            {s.title}
          </Text>
        ))
      ) : (
        <Text style={[type.bodyStrong, { color: allEqual ? colors.text : colors.subtle }]}>
          {allEqual ? 'Все одинаково важны' : emptyText}
        </Text>
      )}
    </Pressable>
  );
}

function Favorites({ me, partner }: { me: Profile; partner: Profile | null }) {
  const rows = partner ? FAVORITES.filter((f) => me[f.key] || partner[f.key]) : [];

  if (!rows.length) {
    return (
      <Card style={{ gap: 12 }}>
        <View style={styles.inlineRow}>
          <Icon name="restaurant-outline" size={20} />
          <Text style={[type.bodyStrong, { color: colors.text, flex: 1 }]}>
            Заполните профиль — и здесь появится ваше любимое
          </Text>
        </View>
        <Pressable accessibilityRole="button" onPress={() => router.push('/profile')} style={styles.inlineRow}>
          <Icon name="create-outline" size={18} />
          <Text style={[type.bodyStrong, { color: colors.text }]}>Заполнить профиль</Text>
        </Pressable>
      </Card>
    );
  }

  return (
    <Card style={{ gap: 0, paddingVertical: 8 }}>
      <View style={styles.favRow}>
        <Text style={styles.favLabel} />
        <Text style={[type.caption, styles.favCell, { color: colors.muted }]}>{me.name}</Text>
        <Text style={[type.caption, styles.favCell, { color: colors.muted }]}>{partner!.name}</Text>
      </View>
      {rows.map((f) => (
        <View key={f.key} style={[styles.favRow, styles.favDivider]}>
          <Text style={[type.caption, styles.favLabel, { color: colors.muted }]}>{f.label}</Text>
          <FavoriteValue value={me[f.key]} isColor={f.key === 'favorite_color'} />
          <FavoriteValue value={partner![f.key]} isColor={f.key === 'favorite_color'} />
        </View>
      ))}
    </Card>
  );
}

function FavoriteValue({ value, isColor }: { value: string | null; isColor: boolean }) {
  const dot = isColor ? colorOf(value) : null;
  return (
    <View style={[styles.favCell, { flexDirection: 'row', alignItems: 'center', gap: 6 }]}>
      {dot ? <View style={[styles.colorDot, { backgroundColor: dot }]} /> : null}
      <Text style={[type.body, { color: value ? colors.text : colors.subtle, flexShrink: 1 }]}>
        {value ? value.charAt(0).toUpperCase() + value.slice(1) : '—'}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  hero: { padding: 20, gap: 4 },
  heroTop: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  heroAvatar: { borderWidth: 2, borderColor: colors.black },
  heroAvatarEmpty: {
    width: 28,
    height: 28,
    borderRadius: 14,
    marginLeft: -8,
    borderStyle: 'dashed',
    borderColor: 'rgba(255,255,255,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  heroLabel: { color: 'rgba(255,255,255,0.7)', flex: 1 },
  heroNumberRow: { flexDirection: 'row', alignItems: 'flex-start', marginTop: space.sm },
  heroButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    alignSelf: 'flex-start',
    backgroundColor: '#fff',
    borderRadius: radius.sm,
    paddingHorizontal: 14,
    height: 40,
    marginTop: space.sm,
  },
  soonRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 6 },
  soonIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  inlineEmpty: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 20 },
  inlineRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  twoCols: { flexDirection: 'row', gap: 12 },
  person: {
    flex: 1,
    gap: 4,
    padding: space.md,
    borderRadius: radius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.background,
  },
  personTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 },
  personMissing: { borderStyle: 'dashed', borderColor: colors.subtle },
  missingIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  petName: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  loveCard: { flexDirection: 'row', gap: space.md, padding: 20 },
  vDivider: { width: 1, backgroundColor: colors.surface2 },
  favRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12 },
  favDivider: { borderTopWidth: 1, borderTopColor: colors.border },
  favLabel: { width: 72 },
  favCell: { flex: 1 },
  colorDot: { width: 10, height: 10, borderRadius: 5, borderWidth: 1, borderColor: colors.border },
});
