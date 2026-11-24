import { router } from 'expo-router';
import { useState } from 'react';

import { Button, Chip, ChipRow, ErrorText, Input, Label, Screen } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { BUDGETS, CUISINES, FORMATS, keysOf, TIMES } from '@/lib/labels';
import type { Budget, Cuisine, Format, TimeOfDay } from '@/lib/types';

export default function NewIdeaScreen() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [format, setFormat] = useState<Format | null>(null);
  const [cuisine, setCuisine] = useState<Cuisine | null>(null);
  const [budget, setBudget] = useState<Budget | null>(null);
  const [times, setTimes] = useState<TimeOfDay[]>([]);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function save() {
    if (!format) return;
    setError('');
    setSaving(true);
    try {
      await api('/couple/ideas', {
        method: 'POST',
        json: {
          title: title.trim(),
          description: description.trim() || null,
          format,
          cuisine: format === 'food' ? cuisine : null,
          budget,
          times_of_day: times,
        },
      });
      router.back();
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  return (
    <Screen topInset={false}>
      <Input label="Что хотите сделать?" value={title} onChangeText={setTitle} placeholder="Сходить на каток" />
      <Input
        label="Подробности (необязательно)"
        value={description}
        onChangeText={setDescription}
        placeholder="Где, с кем, что взять с собой"
        multiline
        style={{ minHeight: 80, paddingTop: 12, textAlignVertical: 'top' }}
      />

      <Label>Формат</Label>
      <ChipRow>
        {keysOf(FORMATS).map((key) => (
          <Chip key={key} label={FORMATS[key]} selected={format === key} onPress={() => setFormat(key)} />
        ))}
      </ChipRow>

      {format === 'food' ? (
        <>
          <Label>Кухня</Label>
          <ChipRow>
            {keysOf(CUISINES).map((key) => (
              <Chip
                key={key}
                label={CUISINES[key]}
                selected={cuisine === key}
                onPress={() => setCuisine(cuisine === key ? null : key)}
              />
            ))}
          </ChipRow>
        </>
      ) : null}

      <Label>Бюджет</Label>
      <ChipRow>
        {keysOf(BUDGETS).map((key) => (
          <Chip
            key={key}
            label={BUDGETS[key]}
            selected={budget === key}
            onPress={() => setBudget(budget === key ? null : key)}
          />
        ))}
      </ChipRow>

      <Label>Когда (можно несколько, или ничего — значит, в любое время)</Label>
      <ChipRow>
        {keysOf(TIMES).map((key) => (
          <Chip
            key={key}
            label={TIMES[key]}
            selected={times.includes(key)}
            onPress={() =>
              setTimes(times.includes(key) ? times.filter((t) => t !== key) : [...times, key])
            }
          />
        ))}
      </ChipRow>

      <ErrorText>{error}</ErrorText>
      <Button title="Сохранить" onPress={save} loading={saving} disabled={!title.trim() || !format} />
    </Screen>
  );
}
