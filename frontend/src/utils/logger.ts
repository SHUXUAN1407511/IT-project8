const isDev = import.meta.env.DEV;

type LogArgs = unknown[];

const emit = (fn: (...args: LogArgs) => void, args: LogArgs) => {
  if (isDev) {
    fn(...args);
  }
};

export const logger = {
  info: (...args: LogArgs) => emit(console.info, args),
  warn: (...args: LogArgs) => emit(console.warn, args),
  error: (...args: LogArgs) => emit(console.error, args),
};

