import { router } from 'expo-router';
import { useState } from 'react';

import { useAuth } from '@/auth/auth-context';
import { Button, DateInput, ErrorText, Input, Screen, Subtitle } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { inputToIso, isoToInput } from '@/lib/dates';

export default function CoupleEditScreen() {
  const { couple, refresh } = useAuth();
  const [name, setName] = useState(couple?.name ?? '');
  const [since, setSince] = useState(isoToInput(couple?.together_since ?? null));
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function save() {
    setError('');
    const sinceIso = since ? inputToIso(since) : null;
    if (since && !sinceIso) {
      setError('Дата — в формате ДД.ММ.ГГГГ');
      return;
    }
    setSaving(true);
    try {
      await api('/couple', {
        method: 'PATCH',
        json: { name: name.trim() || null, together_since: sinceIso },
      });
      await refresh();
      router.back();
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  return (
    <Screen topInset={false}>
      <Input label="Название пары" value={name} onChangeText={setName} placeholder="Например, Мила и Саша" />
      <DateInput label="Вместе с" value={since} onChangeText={setSince} />
      <Subtitle>По этой дате приложение считает, сколько дней вы вместе, и напомнит о годовщине.</Subtitle>
      <ErrorText>{error}</ErrorText>
      <Button title="Сохранить" onPress={save} loading={saving} />
    </Screen>
  );
}
