import { router, useFocusEffect } from 'expo-router';
import { type ReactNode, useCallback, useState } from 'react';
import { View } from 'react-native';

import { api } from '@/lib/api';

import { IconButton, Title } from './ui';

/** Big page title with the notifications bell on the right. */
export function TabHeader({ title, right }: { title: string; right?: ReactNode }) {
  const [unread, setUnread] = useState(0);

  // Refresh the number on the bell whenever the page is opened.
  useFocusEffect(
    useCallback(() => {
      api<{ unread: number }>('/notifications/unread-count')
        .then((r) => setUnread(r.unread))
        .catch(() => {});
    }, []),
  );

  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', minHeight: 56 }}>
      <Title>{title}</Title>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 20 }}>
        {right}
        <IconButton
          name="notifications-outline"
          label="Уведомления"
          badge={unread}
          onPress={() => router.push('/notifications')}
        />
      </View>
    </View>
  );
}
