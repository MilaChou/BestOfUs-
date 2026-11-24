import { Image, type ImageStyle } from 'expo-image';
import type { StyleProp } from 'react-native';

import { authHeaders, serverUrl } from '@/lib/api';

/** A photo from our server: it's private, so the login token is sent with the request. */
export function AuthImage({ path, style }: { path: string; style?: StyleProp<ImageStyle> }) {
  return (
    <Image
      source={{ uri: serverUrl(path), headers: authHeaders() }}
      style={style}
      contentFit="cover"
      transition={150}
    />
  );
}
