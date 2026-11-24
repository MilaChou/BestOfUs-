import { useEffect, useState } from 'react';
import { StyleSheet, Switch, Text, View } from 'react-native';

import { colors, space } from '@/components/theme';
import { Card, ErrorText, Loading, Screen, Subtitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { keysOf, NOTIFICATION_CATEGORIES } from '@/lib/labels';
import type { NotificationCategory } from '@/lib/types';

type Settings = Record<NotificationCategory, boolean>;

export default function NotificationSettingsScreen() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api<Settings>('/notifications/settings').then(setSettings).catch((e) => setError(errorMessage(e)));
  }, []);

  async function toggle(key: NotificationCategory, value: boolean) {
    setSettings((s) => (s ? { ...s, [key]: value } : s)); // show the change right away
    try {
      setSettings(await api<Settings>('/notifications/settings', { method: 'PATCH', json: { [key]: value } }));
    } catch (e) {
      setSettings((s) => (s ? { ...s, [key]: !value } : s)); // undo if the server refused
      setError(errorMessage(e));
    }
  }

  if (!settings) return <Screen topInset={false}>{error ? <ErrorText>{error}</ErrorText> : <Loading />}</Screen>;

  return (
    <Screen topInset={false}>
      <Subtitle>
        Выключенные пуши не придут на телефон, но уведомление всё равно появится в списке под колокольчиком.
      </Subtitle>
      <Card style={{ paddingVertical: space.xs }}>
        {keysOf(NOTIFICATION_CATEGORIES).map((key) => (
          <View key={key} style={styles.row}>
            <Text style={styles.label}>{NOTIFICATION_CATEGORIES[key]}</Text>
            <Switch
              value={settings[key]}
              onValueChange={(v) => toggle(key, v)}
              trackColor={{ true: colors.black, false: colors.border }}
              thumbColor="#fff"
            />
          </View>
        ))}
      </Card>
      <ErrorText>{error}</ErrorText>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 10 },
  label: { fontSize: 16, color: colors.text, flex: 1 },
});
