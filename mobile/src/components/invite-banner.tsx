import * as Clipboard from 'expo-clipboard';
import { useState } from 'react';
import { Pressable, Share, StyleSheet, Text, View } from 'react-native';

import { useAuth, usePartner } from '@/auth/auth-context';

import { colors, radius, space, type } from './theme';
import { Button, Card, Icon } from './ui';

/** Shown until the partner joins: the code to send them. */
export function InviteBanner() {
  const { couple } = useAuth();
  const partner = usePartner();
  const [copied, setCopied] = useState(false);
  if (partner || !couple?.invite_code) return null;

  const code = couple.invite_code;

  async function copy() {
    await Clipboard.setStringAsync(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <Card style={{ gap: 12 }}>
      <View style={styles.top}>
        <View style={styles.icon}>
          <Icon name="person-add-outline" size={18} color={colors.heart} />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={[type.bodyStrong, { color: colors.text }]}>Отправьте этот код партнёру</Text>
          <Text style={[type.caption, { color: colors.muted }]}>Введёт код — и вы пара</Text>
        </View>
      </View>

      <Pressable accessibilityRole="button" accessibilityLabel="Скопировать код" onPress={copy} style={styles.code}>
        <Text selectable style={[type.code, { color: colors.text, flex: 1 }]}>
          {code}
        </Text>
        <Icon name={copied ? 'checkmark' : 'copy-outline'} size={20} color={colors.muted} />
      </Pressable>
      {copied ? <Text style={[type.caption, { color: colors.muted }]}>Код скопирован</Text> : null}

      <Button
        title="Отправить код"
        icon="share-social-outline"
        onPress={() => Share.share({ message: `Присоединяйся ко мне в BestOfUs. Код нашей пары: ${code}` })}
      />
    </Card>
  );
}

const styles = StyleSheet.create({
  top: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  icon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.heartSoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  code: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space.sm,
    paddingHorizontal: space.md,
    paddingVertical: 10,
    borderRadius: radius.md,
    borderWidth: 1.5,
    borderStyle: 'dashed',
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
});
