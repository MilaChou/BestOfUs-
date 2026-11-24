import { useState } from 'react';

import { useAuth } from '@/auth/auth-context';
import { colors } from '@/components/theme';
import { Button, Icon, Screen, Subtitle, Title } from '@/components/ui';
import { SERVER_URL } from '@/lib/api';

export default function OfflineScreen() {
  const { startError, retryStart } = useAuth();
  const [loading, setLoading] = useState(false);

  return (
    <Screen>
      <Icon name="cloud-offline-outline" size={40} color={colors.muted} />
      <Title>Нет связи</Title>
      <Subtitle>{startError}</Subtitle>
      <Subtitle>Адрес сервера: {SERVER_URL}</Subtitle>
      <Button
        title="Попробовать снова"
        loading={loading}
        onPress={async () => {
          setLoading(true);
          await retryStart();
          setLoading(false);
        }}
      />
    </Screen>
  );
}
