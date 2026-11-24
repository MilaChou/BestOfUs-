import type { ComponentProps } from 'react';
import { Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { formatPrice } from '@/lib/dates';
import { GIFT_TYPES, PRIORITIES } from '@/lib/labels';
import type { GiftNote, Wish } from '@/lib/types';

import { colors, space } from './theme';
import { Card, Icon } from './ui';

/** A wish. `mine`: the owner's view (can mark "received"); otherwise the partner's view (can reserve). */
export function WishCard({
  wish,
  mine,
  onPress,
  onToggleReceived,
  onToggleReserve,
}: {
  wish: Wish;
  mine: boolean;
  onPress?: () => void;
  onToggleReceived?: () => void;
  onToggleReserve?: () => void;
}) {
  const meta = [formatPrice(wish.price), wish.gift_type ? GIFT_TYPES[wish.gift_type] : null].filter(Boolean);

  return (
    <Pressable onPress={onPress} disabled={!onPress}>
      <Card>
        <View style={styles.top}>
          <Text style={[styles.title, wish.is_received && styles.done]}>{wish.title}</Text>
          {wish.priority === 'burning' ? <Icon name="flame-outline" size={18} color={colors.heart} /> : null}
        </View>
        <Text style={styles.priority}>{PRIORITIES[wish.priority]}</Text>
        {wish.note ? <Text style={styles.note}>{wish.note}</Text> : null}
        {meta.length ? <Text style={styles.meta}>{meta.join('  ·  ')}</Text> : null}
        <View style={styles.actions}>
          {wish.link ? (
            <Action icon="link-outline" label="Открыть ссылку" onPress={() => Linking.openURL(wish.link!)} />
          ) : null}
          {mine && onToggleReceived ? (
            <Action
              icon={wish.is_received ? 'arrow-undo-outline' : 'checkmark-circle-outline'}
              label={wish.is_received ? 'Ещё не подарили' : 'Мне подарили'}
              onPress={onToggleReceived}
            />
          ) : null}
          {!mine && wish.is_received ? <Text style={styles.meta}>Уже подарено</Text> : null}
          {!mine && !wish.is_received && onToggleReserve ? (
            <Action
              icon={wish.is_reserved ? 'gift' : 'gift-outline'}
              label={wish.is_reserved ? 'Вы подарите · отменить' : 'Я подарю'}
              onPress={onToggleReserve}
              strong={!wish.is_reserved}
            />
          ) : null}
        </View>
      </Card>
    </Pressable>
  );
}

export function NoteCard({ note, onPress, onToggle }: { note: GiftNote; onPress: () => void; onToggle: () => void }) {
  return (
    <Pressable onPress={onPress}>
      <Card>
        <Text style={[styles.title, note.is_gifted && styles.done]}>{note.title}</Text>
        {note.note ? <Text style={styles.note}>{note.note}</Text> : null}
        {note.price !== null || note.gift_type ? (
          <Text style={styles.meta}>
            {[formatPrice(note.price), note.gift_type ? GIFT_TYPES[note.gift_type] : null].filter(Boolean).join('  ·  ')}
          </Text>
        ) : null}
        <View style={styles.actions}>
          <Action
            icon={note.is_gifted ? 'arrow-undo-outline' : 'checkmark-circle-outline'}
            label={note.is_gifted ? 'Ещё не подарено' : 'Подарено'}
            onPress={onToggle}
          />
        </View>
      </Card>
    </Pressable>
  );
}

function Action({
  icon,
  label,
  onPress,
  strong = false,
}: {
  icon: ComponentProps<typeof Icon>['name'];
  label: string;
  onPress: () => void;
  strong?: boolean;
}) {
  return (
    <Pressable accessibilityRole="button" onPress={onPress} hitSlop={8} style={styles.action}>
      <Icon name={icon} size={18} />
      <Text style={[styles.actionText, strong && { textDecorationLine: 'underline' }]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  top: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  title: { flex: 1, fontSize: 17, fontWeight: '600', color: colors.text },
  done: { textDecorationLine: 'line-through', color: colors.muted },
  priority: { fontSize: 13, color: colors.muted },
  note: { fontSize: 15, color: colors.text, lineHeight: 21 },
  meta: { fontSize: 13, color: colors.muted },
  actions: { flexDirection: 'row', flexWrap: 'wrap', gap: space.lg, paddingTop: 4 },
  action: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  actionText: { fontSize: 14, fontWeight: '600', color: colors.text },
});
