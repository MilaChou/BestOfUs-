import * as ImagePicker from 'expo-image-picker';
import { Platform } from 'react-native';

import { api } from './api';
import type { Memory } from './types';

/** Let the user pick photos from the gallery. Returns [] if they cancel. */
export async function pickPhotos(limit: number): Promise<ImagePicker.ImagePickerAsset[]> {
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ['images'],
    allowsMultipleSelection: true,
    selectionLimit: limit,
    quality: 0.8,
  });
  return result.canceled ? [] : result.assets.slice(0, limit);
}

/** Upload picked photos to a memory; returns the updated memory. */
export async function uploadPhotos(memoryId: number, assets: ImagePicker.ImagePickerAsset[]): Promise<Memory> {
  const form = new FormData();
  assets.forEach((asset, i) => {
    const name = asset.fileName ?? `photo-${i}.jpg`;
    if (Platform.OS === 'web' && asset.file) {
      form.append('files', asset.file, name); // the browser gives a real File
    } else {
      // On the phone, React Native reads the file from this local address.
      form.append('files', { uri: asset.uri, name, type: asset.mimeType ?? 'image/jpeg' } as unknown as Blob);
    }
  });
  return api<Memory>(`/couple/memories/${memoryId}/photos`, { method: 'POST', multipart: form });
}
