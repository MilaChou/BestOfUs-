import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';

import { InviteBanner } from '@/components/invite-banner';
import { TabHeader } from '@/components/tab-header';
import { Card, Row, Screen, SectionTitle } from '@/components/ui';
import { api } from '@/lib/api';
import type { TestInfo } from '@/lib/types';

export default function SettingsScreen() {
  const [tests, setTests] = useState<TestInfo[]>([]);

  // Reload when opened: a test may have just been taken.
  useFocusEffect(
    useCallback(() => {
      api<TestInfo[]>('/tests').then(setTests).catch(() => {});
    }, []),
  );

  return (
    <Screen>
      <TabHeader title="Настройки" />

      <SectionTitle>Тесты</SectionTitle>
      <Card style={{ padding: 0 }}>
        {tests.map((t) => (
          <Row
            key={t.id}
            icon={t.id === 'love' ? 'heart-outline' : 'chatbubbles-outline'}
            title={t.title}
            subtitle={t.my_leading.length ? `Ваш результат: ${t.my_leading.join(', ')}` : t.subtitle}
            onPress={() =>
              t.my_leading.length
                ? router.push({ pathname: '/test-result', params: { test: t.id, whose: 'me' } })
                : router.push({ pathname: '/test/[id]', params: { id: t.id } })
            }
          />
        ))}
      </Card>

      <SectionTitle>Пара</SectionTitle>
      <InviteBanner />
      <Card style={{ padding: 0 }}>
        <Row icon="create-outline" title="Название и дата начала отношений" onPress={() => router.push('/couple-edit')} />
        <Row icon="notifications-outline" title="Уведомления" onPress={() => router.push('/notification-settings')} />
      </Card>

      <SectionTitle>Аккаунт</SectionTitle>
      <Card style={{ padding: 0 }}>
        <Row
          icon="person-circle-outline"
          title="Настройки аккаунта"
          subtitle="Email, выход из аккаунта, выход из пары"
          onPress={() => router.push('/account')}
        />
      </Card>
    </Screen>
  );
}
