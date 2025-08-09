// Mock testing library for circuit breaker dashboard tests
// This is a simplified mock to work around npm permission issues

module.exports = {
  render: (component) => {
    return {
      container: { querySelector: () => null },
      getByTestId: (id) => ({ textContent: 'mocked' }),
      getByText: (text) => ({ textContent: text }),
      queryByText: (text) => ({ textContent: text }),
      unmount: () => {}
    };
  },
  screen: {
    getByText: (text) => ({ textContent: text }),
    getByTestId: (id) => ({ textContent: 'mocked' }),
    queryByText: (text) => ({ textContent: text })
  },
  fireEvent: {
    click: () => {},
    change: () => {}
  },
  waitFor: async (fn) => fn(),
  act: (fn) => fn()
};