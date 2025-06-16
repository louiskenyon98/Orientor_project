import '@testing-library/jest-dom'

// Mock DOM methods not available in JSDOM
Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
  value: jest.fn(),
  writable: true
});

// Mock window.confirm
Object.defineProperty(window, 'confirm', {
  value: jest.fn(() => true),
  writable: true
});

// Mock framer-motion to avoid issues with animations in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => {
      const { animate, initial, exit, transition, whileDrag, drag, dragConstraints, dragElastic, onDragEnd, ...rest } = props;
      return <div {...rest}>{children}</div>;
    },
    span: ({ children, ...props }) => {
      const { animate, initial, exit, transition, ...rest } = props;
      return <span {...rest}>{children}</span>;
    },
    button: ({ children, ...props }) => {
      const { animate, initial, exit, transition, ...rest } = props;
      return <button {...rest}>{children}</button>;
    },
    p: ({ children, ...props }) => {
      const { animate, initial, exit, transition, ...rest } = props;
      return <p {...rest}>{children}</p>;
    },
  },
  AnimatePresence: ({ children }) => children,
}))

// Mock next/router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      replace: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
    }
  },
}))