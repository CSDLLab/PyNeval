import importlib
import argparse
import Utils

class Parser:
    def __init__(self):
        ## Parse command line parameters
        parser = argparse.ArgumentParser(description='Gan Framework.')
        subparsers = parser.add_subparsers(help='subcomand description.')

        parser_train = subparsers.add_parser('train', help='start training a mode..')
        parser_continue = subparsers.add_parser('continue', help='continue training a model.')
        parser_test = subparsers.add_parser('test', help='test a model.')

        parser_train.add_argument(
                '-m',
                metavar='model_directory_name',
                nargs=1,
                required=True,
                help='model directory name located under "model" directory')
        parser_train.add_argument(
        		'-e',
        		metavar='extra_comment',
        		nargs=1,
                help='extra comment about this experiment')
        parser_train.set_defaults(func=self.trainParser)


        parser_continue.add_argument(
                '-m',
                metavar='model_directory_name',
                nargs=1,
                required=True,
                help='model directory name located under "model" directory')
        parser_continue.add_argument(
                '-d',
                metavar='experiment_dir',
                nargs=1,
                required=True,
                help='experiment directory name located under "output" directory')
        parser_continue.add_argument(
        		'-s',
        		metavar='step',
        		type=int,
        		nargs=1,
                help='continue from specified step, if not given use the latest checkpoint')
        parser_continue.add_argument(
                '-n',
                action='store_true',
                help='whether write tensorboard log to new directory, if not specified: false')
        parser_continue.add_argument(
        		'-e',
        		metavar='extra_comment',
        		nargs=1,
                help='extra comment about this experiment, only work when -n is set true')


        parser_continue.set_defaults(func=self.finetuneParser)

        parser_test.add_argument(
                '-m',
                metavar='model_directory_name',
                nargs=1,
                required=True,
                help='model directory name located under "model" directory')
        parser_test.add_argument(
                '-d',
                metavar='experiment_dir',
                nargs=1,
                required=True,
                help='experiment directory name located under "output" directory')
        parser_test.add_argument(
                '-s',
                metavar='step',
                nargs=1,
                help='continue from specified step, if not given use the latest checkpoint')
        parser_test.add_argument(
                '-p',
                metavar='test_type',
                nargs=1,
                required=True,
                help='1.generate fake images. 2.given input generate output')
		parser_test.add_argument(
                '-f',
                metavar='folder',
                nargs=1,
                help='input folder to process, should be a path')
        parser_test.set_defaults(func=self.testParser)

        self.parser = parser
        # 用于存放配置信息
        self.env = None

    def parseArgs(self):
        self.args = self.parser.parse_args()
        self.args.func(self.args)
        return self.env

    def commonParser(self, args):
        ## load model package
        model_dir_name = args.m[0]
        model_path = 'model.{}.model'.format(model_dir_name)
        model_factory = importlib.import_module(model_path)

        ## load config file
        config_file_path = 'model/{}/config.json'.format(model_dir_name)
        config_data = Utils.json2dict(config_file_path)
        self.env = model_factory.Environment(config_data)

        ## create root directory
        Utils.setDir(self.env.root_dir)

        ## 设置其他环境变量
        self.env.config_file_path = config_file_path
        self.env.model_dir_name = model_dir_name
        self.env.model_factory = model_factory

    def trainParser(self, args):
        self.commonParser(args)

        self.env.do_train = True
        self.env.continue_from_pre = False
        extra_comment = None
        if args.e:
            extra_comment = args.e[0]

        exp_dir = Utils.generate_expid(self.env.model_dir_name, extra_comment)
        self.env.exp_dir_path = '/'.join([self.env.root_dir,exp_dir])
        Utils.resetDir(self.env.exp_dir_path)

        self.env.log_dir_path = '/'.join([self.env.exp_dir_path,self.env.log_dir])
        Utils.setDir(self.env.log_dir_path)

        self.env.checkpoint_dir_path= '/'.join([self.env.exp_dir_path,self.env.checkpoint_dir])
        Utils.setDir(self.env.checkpoint_dir_path)

        self.env.specified_checkpoint_dir_path= '/'.join([self.env.exp_dir_path,self.env.specified_checkpoint_dir])
        Utils.setDir(self.env.specified_checkpoint_dir_path)

    def finetuneParser(self, args):
        self.commonParser(args)

        self.env.do_train = True
        self.env.continue_from_pre = True

        if args.n: # generate
            old_exp_dir = args.d[0]

            extra_comment = None
            if args.e:
                extra_comment = args.e[0]
            new_exp_dir = Utils.generate_expid(self.env.model_dir_name, extra_comment)
            old_exp_path = '/'.join([self.env.root_dir,old_exp_dir])
            new_exp_path = '/'.join([self.env.root_dir,new_exp_dir])
            Utils.setDir(new_exp_path)
            os.system('cp -r %s/*  %s'%(old_exp_path,new_exp_path))
            self.env.exp_dir_path = new_exp_path
            Utils.testDir(self.env.exp_dir_path)
        else:
            exp_dir = args.d[0]
            self.env.exp_dir_path = '/'.join([self.env.root_dir,exp_dir])
            Utils.testDir(self.env.exp_dir_path)


        self.env.log_dir_path = '/'.join([self.env.exp_dir_path,self.env.log_dir])
        Utils.testDir(self.env.log_dir_path)

        self.env.checkpoint_dir_path= '/'.join([self.env.exp_dir_path,self.env.checkpoint_dir])
        Utils.testDir(self.env.checkpoint_dir_path)

        self.env.specified_checkpoint_dir_path= '/'.join([self.env.exp_dir_path,self.env.specified_checkpoint_dir])
        Utils.testDir(self.env.specified_checkpoint_dir_path)

        self.env.restore_step=None
        if args.s:
            self.env.restore_step = args.s[0]

    def testParser(self, args):
        self.commonParser(args)

        self.env.do_train = False
        self.env.continue_from_pre = True

        exp_dir = args.d[0]
        self.env.exp_dir_path = '/'.join([self.env.root_dir,exp_dir])
        Utils.testDir(self.env.exp_dir_path)


        self.env.log_dir_path = '/'.join([self.env.exp_dir_path,self.env.log_dir])
        Utils.testDir(self.env.log_dir_path)

        self.env.checkpoint_dir_path= '/'.join([self.env.exp_dir_path,self.env.checkpoint_dir])
        Utils.testDir(self.env.checkpoint_dir_path)

        self.env.specified_checkpoint_dir_path= '/'.join([self.env.exp_dir_path,self.env.specified_checkpoint_dir])
        Utils.testDir(self.env.specified_checkpoint_dir_path)

        self.env.test_type = args.p[0]
        self.env.restore_step=None
        if args.s:
            self.env.restore_step = args.s[0]

        self.env.in_folder_path=None
        if args.f:
            self.env.in_folder_path = args.f[0]
