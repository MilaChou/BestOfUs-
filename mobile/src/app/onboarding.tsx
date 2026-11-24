import { useState } from 'react';

import { useAuth } from '@/auth/auth-context';
import {
  Button,
  DateInput,
  ErrorText,
  Input,
  Screen,
  Subtitle,
  Title,
} from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { inputToIso } from '@/lib/dates';

/** Right after registration: a few things about you. Everything is optional. */
export default function OnboardingScreen() {
  const { user, refresh, finishOnboarding } = useAuth();
  const [birthDate, setBirthDate] = useState('');
  const [petName, setPetName] = useState('');
  const [flowers, setFlowers] = useState('');
  const [drink, setDrink] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function save() {
    setError('');
    const birth = birthDate ? inputToIso(birthDate) : null;
    if (birthDate && !birth) {
      setError('Дата рождения — в формате ДД.ММ.ГГГГ');
      return;
    }
    setSaving(true);
    try {
      await api('/users/me/profile', {
        method: 'PATCH',
        json: {
          birth_date: birth,
          pet_name: petName.trim() || null,
          favorite_flowers: flowers.trim() || null,
          favorite_drink: drink.trim() || null,
        },
      });
      await refresh();
      finishOnboarding();
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  return (
    <Screen>
      <Title>Расскажите о себе</Title>
      <Subtitle>
        {user?.profile.name}, это поможет партнёру не забыть важное и выбирать подарки. Всё
        можно заполнить или поменять потом в профиле.
      </Subtitle>
      <DateInput label="Дата рождения" value={birthDate} onChangeText={setBirthDate} />
      <Input
        label="Ласковое имя"
        value={petName}
        onChangeText={setPetName}
        placeholder="Как вас называет партнёр"
      />
      <Input label="Любимые цветы" value={flowers} onChangeText={setFlowers} placeholder="Пионы" />
      <Input label="Любимый напиток" value={drink} onChangeText={setDrink} placeholder="Матча латте" />
      <ErrorText>{error}</ErrorText>
      <Button title="Продолжить" onPress={save} loading={saving} />
      <Button title="Заполню позже" variant="ghost" onPress={finishOnboarding} disabled={saving} />
    </Screen>
  );
}
