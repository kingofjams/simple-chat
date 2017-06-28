class abc:
    sn = []

    @classmethod
    def add_sn(self):
        self.sn.append('a1')

if __name__ == "__main__":
    abc.add_sn()
    abc.add_sn()
    abc.add_sn()
    abc.add_sn()
    abc.add_sn()
    print abc.sn
