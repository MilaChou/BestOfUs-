import { router, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Alert } from 'react-native';

import { useAuth, usePartner } from '@/auth/auth-context';
import { Button, Chip, ChipRow, DateInput, ErrorText, Input, Label, Loading, Screen } from '@/components/ui';
import { api, errorMessage } from '@/lib/api';
import { inputToIso, isoToInput } from '@/lib/dates';
import { keysOf, TASK_CATEGORIES } from '@/lib/labels';
import type { Task, TaskCategory } from '@/lib/types';

/** New plan (no id) or editing an existing one (?id=5). */
export default function TaskScreen() {
  const { id, due: presetDue } = useLocalSearchParams<{ id?: string; due?: string }>();
  const { user } = useAuth();
  const partner = usePartner();
  const [loaded, setLoaded] = useState(!id);
  const [title, setTitle] = useState('');
  const [note, setNote] = useState('');
  const [category, setCategory] = useState<TaskCategory | null>(null);
  const [due, setDue] = useState(presetDue ? isoToInput(presetDue) : '');
  const [assignee, setAssignee] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!id) return;
    api<Task>(`/couple/tasks/${id}`)
      .then((t) => {
        setTitle(t.title);
        setNote(t.note ?? '');
        setCategory(t.category);
        setDue(isoToInput(t.due_date));
        setAssignee(t.assignee_id);
        setLoaded(true);
      })
      .catch((e) => setError(errorMessage(e)));
  }, [id]);

  async function save() {
    setError('');
    const dueIso = due ? inputToIso(due) : null;
    if (due && !dueIso) {
      setError('Дата — в формате ДД.ММ.ГГГГ');
      return;
    }
    setSaving(true);
    const json = { title: title.trim(), note: note.trim() || null, category, due_date: dueIso, assignee_id: assignee };
    try {
      await api(id ? `/couple/tasks/${id}` : '/couple/tasks', { method: id ? 'PATCH' : 'POST', json });
      router.back();
    } catch (e) {
      setError(errorMessage(e));
      setSaving(false);
    }
  }

  function remove() {
    Alert.alert('Удалить план?', `«${title}»`, [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Удалить',
        style: 'destructive',
        onPress: async () => {
          try {
            await api(`/couple/tasks/${id}`, { method: 'DELETE' });
            router.back();
          } catch (e) {
            setError(errorMessage(e));
          }
        },
      },
    ]);
  }

  if (!loaded) return <Screen topInset={false}>{error ? <ErrorText>{error}</ErrorText> : <Loading />}</Screen>;

  return (
    <Screen topInset={false}>
      <Input label="Что нужно сделать" value={title} onChangeText={setTitle} placeholder="Купить продукты" />
      <Input
        label="Заметка"
        value={note}
        onChangeText={setNote}
        placeholder="Молоко, хлеб, яйца"
        multiline
        style={{ minHeight: 80, paddingTop: 12, textAlignVertical: 'top' }}
      />

      <Label>Кто делает</Label>
      <ChipRow>
        <Chip label="Вместе" selected={assignee === null} onPress={() => setAssignee(null)} />
        {user ? <Chip label="Я" selected={assignee === user.id} onPress={() => setAssignee(user.id)} /> : null}
        {partner ? (
          <Chip label={partner.profile.name} selected={assignee === partner.id} onPress={() => setAssignee(partner.id)} />
        ) : null}
      </ChipRow>

      <DateInput label="Срок (необязательно)" value={due} onChangeText={setDue} />

      <Label>Категория</Label>
      <ChipRow>
        {keysOf(TASK_CATEGORIES).map((key) => (
          <Chip
            key={key}
            label={TASK_CATEGORIES[key]}
            selected={category === key}
            onPress={() => setCategory(category === key ? null : key)}
          />
        ))}
      </ChipRow>

      <ErrorText>{error}</ErrorText>
      <Button title="Сохранить" onPress={save} loading={saving} disabled={!title.trim()} />
      {id ? <Button title="Удалить" variant="ghost" icon="trash-outline" onPress={remove} /> : null}
    </Screen>
  );
}
