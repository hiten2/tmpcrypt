#ifndef TMPCRYPT_H
#define TMPCRYPT_H

#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* tmpcrypt - a simple encryption routine */

struct tmpcrypt {
  size_t dki; /* decryption key index */
  size_t eki; /* encryption key index */
  uint8_t *key;
  size_t key_size;
  uint8_t pbox[256];
  uint8_t rpbox[256];
};

static uint8_t tmpcrypt_pbox[256];

/* decrypt a buffer in-place */
int tmpcrypt_decrypt(uint8_t *buf, struct tmpcrypt *cipher, size_t size);

/* encrypt a buffer in-place */
int tmpcrypt_encrypt(uint8_t *buf, struct tmpcrypt *cipher, size_t size);

/* generate the P-Box and reverse P-Box using the cipher's key */
int tmpcrypt_generate_pboxes(struct tmpcrypt *cipher);

int tmpcrypt_init(struct tmpcrypt *cipher, uint8_t *key, size_t key_size);

/* load the default P-Box from a file */
int tmpcrypt_load_default_pbox(char *path);

/* return whether the P-Boxes correspond */
int tmpcrypt_validate_pboxes(struct tmpcrypt *cipher);

#endif
