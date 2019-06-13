#include "tmpcrypt.h"

/* tmpcrypt - light, fast, and now in C */
/////////////////////////////////store key index separately for decryption & encryption
static uint8_t tmpcrypt_pbox[256] = {
  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
  17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
  33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
  49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
  65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
  81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96,
  97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
  112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127,
  128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143,
  144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
  160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175,
  176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
  192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
  208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223,
  224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
  240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255
};

int tmpcrypt_decrypt(uint8_t *buf, struct tmpcrypt *cipher, size_t size) {
  uint8_t c;
  size_t i;
  int retval;

  if (buf == NULL)
    return -EFAULT;

  if (cipher->key == NULL
      && cipher->key_size)
    return -EINVAL;

  if (!cipher->key_size
      || !size)
    return 0;
  retval = tmpcrypt_validate_pboxes(cipher);

  if (retval <= 0)
    return retval < 0 ? retval : -EINVAL;
  i = 0;
  
  while (i < size) {
    while (i < size && cipher->dki < cipher->key_size) {
      /* permute */

      buf[i] = cipher->rpbox[buf[i]];
      
      /* XOR with key */

      buf[i] ^= cipher->key[cipher->dki];
      
      cipher->dki = (cipher->dki + 1) % cipher->key_size;
      i++;
    }
  }
  return 0;
}

int tmpcrypt_encrypt(uint8_t *buf, struct tmpcrypt *cipher, size_t size) {
  uint8_t c;
  size_t i;
  size_t k;
  int retval;

  if (buf == NULL)
    return -EFAULT;

  if (cipher->key == NULL
      && cipher->key_size)
    return -EINVAL;

  if (!cipher->key_size
      || !size)
    return 0;
  retval = tmpcrypt_validate_pboxes(cipher);

  if (retval <= 0)
    return retval < 0 ? retval : -EINVAL;
  i = 0;
  
  while (i < size) {
    while (i < size && cipher->eki < cipher->key_size) {
      /* XOR with key */

      buf[i] ^= cipher->key[cipher->eki];
      
      /* permute */

      buf[i] = cipher->rpbox[buf[i]];
      
      cipher->dki = (cipher->eki + 1) % cipher->key_size;
      i++;
    }
  }
  return 0;
}

int tmpcrypt_init(struct tmpcrypt *cipher, uint8_t *key, size_t key_size) {
  int retval;
  
  if (cipher == NULL)
    return -EFAULT;
  
  if (key == NULL)
    return -EFAULT;
  *cipher = (struct tmpcrypt) {
    .dki = 0,
    .eki = 0,
    .key = key,
    .key_size = key_size
  };
  
  /* generate P-Boxes */
  
  retval = tmpcrypt_generate_pboxes(cipher);
  
  if (retval)
    /* clean */
    
    *cipher = (struct tmpcrypt) {
      .key = NULL,
      .key_size = 0
    };
  return retval;
}

int tmpcrypt_generate_pboxes(struct tmpcrypt *cipher) {
  uint8_t k;
  size_t i;
  size_t j;
  uint8_t temp;

  if (cipher == NULL)
    return -EFAULT;

  if (cipher->key == NULL
      && cipher->key_size)
    return -EINVAL;

  /* generate forward P-Box */

  memcpy(cipher->pbox, tmpcrypt_pbox, 256);

  for (i = 0; i < cipher->key_size; i++) {
    k = cipher->key[i];

    /* whirlpool permutation algorithm */

    if (k) {
      temp = cipher->pbox[k - 1];

      for (j = k - 1; j > 0; j--)
        cipher->pbox[j] = cipher->pbox[j - 1];
      cipher->pbox[0] = temp;
    }

    if (k < 255) {
      temp = cipher->pbox[k + 1];

      for (j = k + 1; j < 255; j++)
        cipher->pbox[j] = cipher->pbox[j + 1];
      cipher->pbox[255] = temp;
    }
  }

  /* generate reverse P-Box */

  memcpy(cipher->rpbox, tmpcrypt_pbox, 256);

  for (i = 0; i < 256; i++)
    cipher->rpbox[cipher->pbox[i]] = i;
  return 0;
}

int tmpcrypt_load_default_pbox(char *path) {
  int fd;
  int retval;
  
  if (path == NULL)
    return -EFAULT;
  fd = open(path, O_RDONLY);
  
  if (fd < 0)
    return -EBADF;
  retval = 0;
  
  if (read(fd, &tmpcrypt_pbox, sizeof(tmpcrypt_pbox)) != sizeof(tmpcrypt_pbox))
    retval = errno ? -errno : -EIO;
  close(fd);
  return retval;
}

int tmpcrypt_validate_pboxes(struct tmpcrypt *cipher) {
  struct tmpcrypt _cipher;
  int retval;

  if (cipher == NULL)
    return -EFAULT;

  if (cipher->key == NULL
      && cipher->key_size)
    return -EINVAL;
  _cipher.key = cipher->key;
  _cipher.key_size = cipher->key_size;
  retval = tmpcrypt_generate_pboxes(&_cipher);

  if (retval) {
    ((void *(* volatile)(void *, int, size_t)) &memset)(&_cipher, '\0', sizeof(_cipher));
    return retval;
  }

  if (memcmp(_cipher.pbox, cipher->pbox, 256)
      || memcmp(_cipher.rpbox, cipher->rpbox, 256))
    return 0;
  ((void *(* volatile)(void *, int, size_t)) &memset)(&_cipher, '\0', sizeof(_cipher));
  return 1;
}
