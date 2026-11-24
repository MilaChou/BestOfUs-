import { router } from 'expo-router';
import { useState } from 'react';

import { useAuth } from '@/auth/auth-context';
import {
  Button,
  DateInput,
  ErrorText,
  Input,
  Screen,
  SectionTitle,
  Subtitle,
} from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { inputToIso, isoToInput } from '@/lib/dates';
import { PROFILE_SECTIONS } from '@/lib/labels';
import type { Profile, ProfileField } from '@/lib/types';

type Draft = Record<ProfileField, string>;

function toDraft(profile: Profile): Draft {
  const draft = {} as Draft;
  for (const section of PROFILE_SECTIONS) {
    for (const { key } of section.fields) {
      draft[key] = key === 'birth_date' ? isoToInput(profile.birth_date) : (profile[key] ?? '');
    }
  }
  return draft;
}

export default function ProfileScreen() {
  const { user, refresh } = useAuth();
  const [draft, setDraft] = useState<Draft>(() => toDraft(user!.profile));
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  function set(key: ProfileField, value: string) {
    setDraft((d) => ({ ...d, [key]: value }));
  }

  async function save() {
    setError('');
    if (!draft.name.trim()) {
      setError('Имя не может быть пустым');
      return;
    }
    const birth = draft.birth_date ? inputToIso(draft.birth_date) : null;
    if (draft.birth_date && !birth) {
      setError('Дата рождения — в формате ДД.ММ.ГГГГ');
      return;
    }
    // Empty fields are sent as null, so they are cleared on the server.
    const json: Record<string, string | null> = {};
    for (const [key, value] of Object.entries(draft)) json[key] = value.trim() || null;
    json.name = draft.name.trim();
    json.birth_date = birth;

    setSaving(true);
    try {
      await api('/users/me/profile', { method: 'PATCH', json });
      await refresh();
      router.back();
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  return (
    <Screen topInset={false}>
      <Subtitle>Партнёр видит ваш профиль — так проще выбирать для вас подарки и заботиться о вас.</Subtitle>
      {PROFILE_SECTIONS.map((section) => (
        <SectionBlock key={section.title} title={section.title}>
          {section.fields.map((field) =>
            field.key === 'birth_date' ? (
              <DateInput
                key={field.key}
                label={field.label}
                value={draft.birth_date}
                onChangeText={(v) => set('birth_date', v)}
              />
            ) : (
              <Input
                key={field.key}
                label={field.label}
                value={draft[field.key]}
                onChangeText={(v) => set(field.key, v)}
                placeholder={field.placeholder}
                multiline={field.multiline}
                style={field.multiline ? { minHeight: 80, paddingTop: 12, textAlignVertical: 'top' } : undefined}
              />
            ),
          )}
        </SectionBlock>
      ))}
      <ErrorText>{error}</ErrorText>
      <Button title="Сохранить" onPress={save} loading={saving} />
    </Screen>
  );
}

function SectionBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <>
      <SectionTitle>{title}</SectionTitle>
      {children}
    </>
  );
}
